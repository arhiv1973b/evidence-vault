document.addEventListener('DOMContentLoaded', () => {
    fetch('manifest.json')
        .then(response => response.json())
        .then(data => {
            const nodes = Array.isArray(data.evidenceNodes) ? data.evidenceNodes : [];

            // Render evidence grid
            const grid = document.getElementById('dynamic-evidence-grid');
            if (grid) {
                grid.innerHTML = nodes.map(node => `
                    <div class="ev-card">
                        <div class="ev-card-icon">${node.icon}</div>
                        <div class="ev-card-title">${node.title}</div>
                        <div class="ev-card-body">
                            ${node.num ? `<span class="num">${node.num}</span>` : ''}
                            ${node.body}
                        </div>
                    </div>
                `).join('');
            }

            const nodeList = document.getElementById('dynamic-node-list');
            if (nodeList) {
                nodeList.innerHTML = nodes.map(node => {
                    const slug = String(node.id || node.title || '').trim();
                    const href = slug ? `nodes/${encodeURI(slug)}.html` : '#';
                    return `<li><a href="${href}">${node.icon ? node.icon + ' ' : ''}${node.title}</a></li>`;
                }).join('');
            }

            // Render forensic data
            const updateField = (id, value, className = '') => {
                const el = document.getElementById(id);
                if (el) {
                    el.textContent = value;
                    if (className) el.className = 'val ' + className;
                }
            };

            updateField('f-subject', data.forensicData.subject, 'gold');
            updateField('f-theftAmount', data.forensicData.theftAmount, 'red');
            updateField('f-subjects', data.forensicData.subjects, 'red');
            updateField('f-method', data.forensicData.method);
            updateField('f-timestamp', data.forensicData.timestamp, 'green');
            updateField('f-merkleRoot', data.forensicData.merkleRoot, 'green');

            const projection = document.getElementById('dynamic-projection');
            if (projection) {
                const projections = Array.isArray(data.projectionNodes) ? data.projectionNodes : [];
                projection.innerHTML = projections.map(item => {
                    const href = item.kind === 'html' ? item.source : item.source;
                    const download = item.download ? ` download="${item.download}"` : '';
                    return `
                        <div class="proj-card">
                            <div class="proj-badge">${item.badge || item.kind}</div>
                            <div class="proj-title">${item.title}</div>
                            <div class="proj-preview">${item.preview || ''}</div>
                            <div class="proj-actions">
                                <a class="proj-btn" href="${href}">Open</a>
                                ${item.download ? `<a class="proj-btn" href="${item.download}"${download}>Download</a>` : ''}
                            </div>
                        </div>
                    `;
                }).join('');
            }
        })
        .catch(err => console.error('Error loading manifest:', err));
});
