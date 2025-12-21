document.addEventListener("DOMContentLoaded", function() {
    
    // 1. MATRIX RAIN
    const canvas = document.getElementById('matrix-canvas');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth; canvas.height = window.innerHeight;
        const chars = 'AES12801XYZ'; const charArray = chars.split('');
        const fontSize = 14; const columns = canvas.width / fontSize;
        const drops = []; for (let x = 0; x < columns; x++) drops[x] = 1;
        function drawMatrix() {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.05)'; ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#0F0'; ctx.font = fontSize + 'px monospace';
            for (let i = 0; i < drops.length; i++) {
                const text = charArray[Math.floor(Math.random() * charArray.length)];
                ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) drops[i] = 0;
                drops[i]++;
            }
        }
        setInterval(drawMatrix, 35);
    }

    // 2. HACKER EFFECT JUDUL ATAS
    const heroTitle = document.getElementById('hero-title-text'); 
    if (heroTitle) {
        const finalText = "AES-128 CUSTOM S-BOX\n(AFFINE MATRIX)"; 
        const characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890@#$%^&*()_+-=[]{}|;':,./<>?"; 
        let iteration = 0; let interval = null;
        heroTitle.setAttribute('data-text', finalText); 
        function startHackingEffect() {
            clearInterval(interval); iteration = 0;
            interval = setInterval(() => {
                heroTitle.innerText = finalText.split("").map((letter, index) => {
                    if(index < iteration) return finalText[index];
                    if(letter === '\n') return '\n'; 
                    return characters[Math.floor(Math.random() * characters.length)];
                }).join("");
                if(iteration >= finalText.length) clearInterval(interval);
                iteration += 1 / 2; 
            }, 30);
        }
        startHackingEffect();
        heroTitle.addEventListener('mouseover', startHackingEffect);
    }

    // 3. SLIDER TEAM
    let next = document.querySelector('.next');
    let prev = document.querySelector('.prev');
    let slide = document.querySelector('.slide');
    if(next && prev && slide) {
        next.addEventListener('click', function(){
            let items = document.querySelectorAll('.item');
            slide.appendChild(items[0]);
        });
        prev.addEventListener('click', function(){
            let items = document.querySelectorAll('.item');
            slide.prepend(items[items.length - 1]);
        });
    }

    // 4. CLICK PHOTO TO SLIDE
    let visuals = document.querySelectorAll('.item .visual');
    visuals.forEach(vis => {
        vis.addEventListener('click', function(){
            let items = document.querySelectorAll('.item');
            slide.appendChild(items[0]);
        });
    });

    // 5. ICARUS RUBBER STRETCH LOGIC (BARU)
    const icarus = document.querySelector('.hanging-icarus');
    if (icarus) {
        // Saat mouse ditekan (klik tahan) -> Tambah class melar
        icarus.addEventListener('mousedown', function() {
            this.classList.add('rubber-active');
            this.style.cursor = 'grabbing'; 
        });

        // Saat mouse dilepas -> Hapus class melar (biar mental balik)
        window.addEventListener('mouseup', function() {
            if (icarus.classList.contains('rubber-active')) {
                icarus.classList.remove('rubber-active');
                icarus.style.cursor = 'grab';
                
                // Efek visual 'boing' saat mental balik
                icarus.animate([
                    { transform: 'translateY(0)' },
                    { transform: 'translateY(-20px)' }, 
                    { transform: 'translateY(10px)' },
                    { transform: 'translateY(0)' }
                ], {
                    duration: 400,
                    easing: 'ease-out'
                });
            }
        });
    }
});