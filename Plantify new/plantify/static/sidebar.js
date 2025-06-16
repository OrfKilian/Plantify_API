document.addEventListener('DOMContentLoaded', function () {
    fetch('/api/items')
        .then(response => response.json())
        .then(data => {
            const potList = document.getElementById('sidebar-pots');
            const plantList = document.getElementById('sidebar-plants');
            potList.innerHTML = '';
            plantList.innerHTML = '';

            const pots = data.pots || [];
            pots.forEach(pot => {
                const li = document.createElement('li');
                const link = document.createElement('a');
                link.href = '#';
                link.innerHTML = `🏺 <span class="sidebar-text">${pot.name}</span>`;
                link.addEventListener('click', function (e) {
                    e.preventDefault();
                    document.querySelectorAll('.sidebar a.active').forEach(el => el.classList.remove('active'));
                    link.classList.add('active');
                });
                li.appendChild(link);
                potList.appendChild(li);
            });

            const plants = data.plants || [];
            const sortOrder = [
                "monstera", "strelitzie", "orchidee", "tomate", "orchidee 2", "monstera 2"
            ];
            plants.sort((a, b) => {
                const aIdx = sortOrder.indexOf(a.name.toLowerCase());
                const bIdx = sortOrder.indexOf(b.name.toLowerCase());
                return (aIdx === -1 ? 99 : aIdx) - (bIdx === -1 ? 99 : bIdx);
            });

            plants.forEach(item => {
                const li = document.createElement('li');
                const link = document.createElement('a');
                link.href = `/pflanze/${item.name.toLowerCase().replace(/\s+/g, '-')}`;
                link.innerHTML = `🪴 <span class="sidebar-text">${item.name}</span>`;
                link.addEventListener('click', function () {
                    document.querySelectorAll('.sidebar a.active').forEach(el => el.classList.remove('active'));
                    link.classList.add('active');
                });
                li.appendChild(link);
                plantList.appendChild(li);
            });
        })
        .catch(error => {
            console.error('Fehler beim Laden der Sidebar:', error);
        });
});
