import os
import json
import subprocess
import datetime
from google import genai
from google.genai.errors import APIError

CONFIG_PATH = "model_gearbox_config.json"

def load_config():
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError(f"Конфигурация не найдена: {CONFIG_PATH}")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    try:
        hub_branch = config.get("hub_branch", "model-hub-sync")
        subprocess.run(["git", "pull", "--rebase", "origin", hub_branch], capture_output=True)
        subprocess.run(["git", "add", CONFIG_PATH], check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Auto-sync: gearbox state update [skip ci]"], capture_output=True)
        subprocess.run(["git", "push", "origin", hub_branch], capture_output=True)
    except Exception as e:
        print(f"[Hub Sync Warning] Не удалось синхронизировать состояние с GitHub: {e}")

def reset_exhausted_gears(config):
    """Сбрасывает статус моделей, если их индивидуальный cooldown истёк."""
    now = datetime.datetime.utcnow()
    for gear_id, gear_info in config["gears"].items():
        if gear_info["status"] == "exhausted" and gear_info.get("exhausted_until"):
            try:
                exhausted_time = datetime.datetime.fromisoformat(gear_info["exhausted_until"])
                delta = (now - exhausted_time).total_seconds()
                cooldown = gear_info.get("cooldown_seconds", 3600)
                if delta >= cooldown:
                    gear_info["status"] = "standby"
                    gear_info["exhausted_until"] = None
                    print(f"[Cooldown Reset] Модель {gear_info['model_name']} возвращена в строй (передача {gear_id}).")
            except Exception as e:
                print(f"[Cooldown Reset Warning] Ошибка обработки времени для передачи {gear_id}: {e}")
    return config

def get_best_available_model(config, recent_failures=0):
    """Выбирает модель с учётом приоритета, веса нагрузки и динамического штрафа ошибок."""
    available_gears = [
        (gear_id, gear_info)
        for gear_id, gear_info in config["gears"].items()
        if gear_info["status"] in ("active", "standby")
    ]
    
    if not available_gears:
        # Страховка от тупика: если исчерпаны абсолютно все, сбрасываем статус в standby
        for gear_id, gear_info in config["gears"].items():
            gear_info["status"] = "standby"
            gear_info["exhausted_until"] = None
        available_gears = [(g_id, g_inf) for g_id, g_inf in config["gears"].items()]

    scored_gears = []
    for gear_id, gear_info in available_gears:
        priority = gear_info.get("priority", 999)
        weight = gear_info.get("load_weight", 1.0)
        score = priority + (weight * recent_failures)
        scored_gears.append((gear_id, gear_info, score))
    
    scored_gears.sort(key=lambda g: g[2])
    best_gear_id, best_info, best_score = scored_gears[0]
    
    config["current_gear"] = int(best_gear_id)
    config["gears"][best_gear_id]["status"] = "active"
    
    print(f"[Hybrid Selector] Выбрана передача {best_gear_id} | Модель: {best_info['model_name']} | Score={best_score:.2f}")
    return best_gear_id, best_info["model_name"]

def shift_gear(config, gear_id):
    gear_info = config["gears"][str(gear_id)]
    gear_info["status"] = "exhausted"
    gear_info["exhausted_until"] = datetime.datetime.utcnow().isoformat()
    print(f"[Gearbox] Передача {gear_id} ({gear_info['model_name']}) исчерпана. Установлен cooldown.")
    save_config(config)
    return config

def execute_with_gearbox(prompt: str):
    client = genai.Client()
    config = load_config()
    
    # 1. Автоматический сброс устаревших кулдаунов перед запуском
    config = reset_exhausted_gears(config)
    save_config(config)
    
    max_attempts = len(config["gears"])
    attempt = 0
    recent_failures = 0
    
    while attempt < max_attempts:
        gear_id, model_name = get_best_available_model(config, recent_failures)
        print(f"[Gearbox] Используется передача {gear_id} | Модель: {model_name}")
        
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            return response.text
            
        except APIError as e:
            if e.code in (429, 503) or "Quota exceeded" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print(f"[Gearbox] Ошибка {e.code} для {model_name}. Переключаем передачу...")
                recent_failures += 1
                config = shift_gear(config, gear_id)
                attempt += 1
            else:
                raise e
        except (TimeoutError, ConnectionError) as e:
            print(f"[Gearbox] Сетевой сбой: {e}. Переключаем передачу...")
            recent_failures += 1
            config = shift_gear(config, gear_id)
            attempt += 1
        except Exception as e:
            raise e
            
    raise RuntimeError("[Gearbox Error] Все доступные модели исчерпали квоты или недоступны.")

if __name__ == "__main__":
    test_prompt = "Диагностика среды: проверь работоспособность через гибридный коммутатор."
    result = execute_with_gearbox(test_prompt)
    print("\n--- Результат выполнения ---")
    print(result)
