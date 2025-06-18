document.addEventListener('DOMContentLoaded', function () {
    fetch('/api/items')
        .then(response => response.json())
        .then(data => {
            const potList = document.getElementById('sidebar-pots');
            const plantList = document.getElementById('sidebar-plants');
            potList.innerHTML = '';
            plantList.innerHTML = '';

            const slugify = str => str.toLowerCase().replace(/\s+/g, '-');

            const rooms = data.rooms || [];
            rooms.forEach(room => {
                const li = document.createElement('li');
                const link = document.createElement('a');
                link.href = `/dashboard/${slugify(room.name)}`;
                link.innerHTML = `🏠 <span class="sidebar-text">${room.name}</span>`;
                li.appendChild(link);
                potList.appendChild(li);
            });

            const plants = data.plants || [];
            plants.forEach(plant => {
                const li = document.createElement('li');
                const link = document.createElement('a');
                link.href = `/pflanze/${slugify(plant.name)}`;
                link.innerHTML = `🪴 <span class="sidebar-text">${plant.name}</span>`;
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
