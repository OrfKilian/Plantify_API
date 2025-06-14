document.addEventListener('DOMContentLoaded', function () {
    fetch('/api/items')
        .then(response => response.json())
        .then(data => {
            // Sortierung wie auf Screenshot 2
            const sortOrder = [
                "monstera", "strelitzie", "orchidee", "tomate", "orchidee 2", "monstera 2"
            ];
            data.sort((a, b) => {
                const aIdx = sortOrder.indexOf(a.name.toLowerCase());
                const bIdx = sortOrder.indexOf(b.name.toLowerCase());
                return (aIdx === -1 ? 99 : aIdx) - (bIdx === -1 ? 99 : bIdx);
            });

            const list = document.getElementById('sidebar-list');
            list.innerHTML = '';

            data.forEach(item => {
                const li = document.createElement('li');
                const link = document.createElement('a');
                link.href = `/pflanze/${item.name.toLowerCase().replace(/\s+/g, '-')}`;

                // Einheitliches, neutrales Icon (🪴)
                link.innerHTML = `🪴 <span class="sidebar-text">${item.name}</span>`;

                li.appendChild(link);
                list.appendChild(li);
            });
        })
        .catch(error => {
            console.error('Fehler beim Laden der Sidebar:', error);
        });
});
