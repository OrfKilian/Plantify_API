document.addEventListener('DOMContentLoaded', function () {
    fetch('/api/items')
        .then(response => response.json())
        .then(data => {
            const potList = document.getElementById('sidebar-pots');
            const plantList = document.getElementById('sidebar-plants');
            potList.innerHTML = '';
            plantList.innerHTML = '';

            const pots = data.plants || [];
            // Reihenfolge wie geliefert anzeigen
            pots.forEach(pot => {
                const li = document.createElement('li');
                const link = document.createElement('a');
                link.href = `/pflanze/${pot.name.toLowerCase().replace(/\s+/g, '-')}`;
                link.innerHTML = `🪴 <span class="sidebar-text">${pot.name}</span>`;
                li.appendChild(link);
                potList.appendChild(li);
            });

            const plants = data.pots || [];

            plants.forEach(item => {
                const li = document.createElement('li');
                const link = document.createElement('a');
                link.href = '#';
                link.innerHTML = `🏺 <span class="sidebar-text">${item.name}</span>`;
                li.appendChild(link);
                plantList.appendChild(li);
            });

            const setActive = (e) => {
                document.querySelectorAll('.sidebar a').forEach(a => a.classList.remove('active'));
                e.currentTarget.classList.add('active');
            };

            document.querySelectorAll('.sidebar a').forEach(a => {
                a.addEventListener('click', setActive);
                if (a.pathname === window.location.pathname) {
                    a.classList.add('active');
                }
            });
        })
        .catch(error => {
            console.error('Fehler beim Laden der Sidebar:', error);
        });
});
