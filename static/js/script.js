document.addEventListener('DOMContentLoaded', () => {

    // --- Anti-Inspection Security ---
    document.addEventListener('contextmenu', event => event.preventDefault());
    document.addEventListener('keydown', (e) => {
        if (e.key === 'F12' || 
            (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'J' || e.key === 'C')) || 
            (e.ctrlKey && e.key === 'U')) {
            e.preventDefault();
        }
    });

    // --- References ---
    const btnGenerateAI = document.getElementById('btn-generate-ai');
    const btnAIText = document.getElementById('btn-ai-text');
    
    // Inputs
    const inputDate = document.getElementById('pyramid-input');
    const inputDream = document.getElementById('dream-input');
    const selectPlayType = document.getElementById('play-type-select');
    
    // Initialize Premium Datepicker (Flatpickr)
    if (inputDate) {
        flatpickr(inputDate, {
            locale: "es", // Spanish localization
            dateFormat: "dmY", // e.g. 13032026 (Backend format)
            altInput: true,
            altFormat: "j F, Y", // e.g. 13 Marzo, 2026 (Beautiful UI format)
            defaultDate: new Date(), // Pre-select today, but show the calendar
            disableMobile: "true" // Force customized UI on mobile devices
        });
    }
    
    // Sequence Logic
    const selectAnimalSeq = document.getElementById('animal-sequence-select');
    const selectTimeSeq = document.getElementById('animal-time-select');
    const btnAddAnimal = document.getElementById('btn-add-animal');
    const tagsContainer = document.getElementById('sequence-tags-container');
    let pastAnimalsList = [];
    
    // View States
    const aiIdleState = document.getElementById('ai-idle-state');
    const aiHeader = document.getElementById('ai-output-header');
    const aiBody = document.getElementById('ai-output-body');
    const uiPlayTypeLabel = document.getElementById('ui-play-type');
    
    // Lottery Target Selector Dynamics
    const selectLottery = document.getElementById('lottery-target-select');
    const containerLottery = document.getElementById('lottery-target-container');
    
    if (selectPlayType && containerLottery) {
        selectPlayType.addEventListener('change', () => {
            if (selectPlayType.value === 'Quiniela') {
                containerLottery.style.display = 'none';
            } else {
                containerLottery.style.display = 'block';
            }
        });
        // Initial check
        if(selectPlayType.value === 'Quiniela') containerLottery.style.display = 'none';
    }
    
    // Dynamic Containers
    const aiDynamicCards = document.getElementById('ai-dynamic-cards-container');
    const eReasoning = document.getElementById('ai-reasoning-text');
    
    // Live Feed Modal
    const feedList = document.getElementById('live-feed-list');
    const btnRefreshFeed = document.getElementById('btn-refresh-feed');
    const btnOpenFeedModal = document.getElementById('btn-open-feed-modal');
    const btnCloseFeedModal = document.getElementById('btn-close-feed-modal');
    const feedModalOverlay = document.getElementById('feed-modal-overlay');
    const feedModalContent = document.getElementById('feed-modal-content');
    
    // Mini Simulator
    const btnRandom = document.getElementById('btn-random-mini');
    const randomResult = document.getElementById('random-result');
    
    // Scroll-to-Top Button
    const btnScrollTop = document.getElementById('btn-scroll-top');
    
    // --- Modal Logic ---
    const openFeedModal = () => {
        if(feedModalOverlay) {
            feedModalOverlay.classList.remove('opacity-0', 'pointer-events-none');
            if(feedModalContent) feedModalContent.classList.remove('scale-95');
        }
    };
    
    const closeFeedModal = () => {
        if(feedModalOverlay) {
            feedModalOverlay.classList.add('opacity-0', 'pointer-events-none');
            if(feedModalContent) feedModalContent.classList.add('scale-95');
        }
    };

    if(btnOpenFeedModal) btnOpenFeedModal.addEventListener('click', openFeedModal);
    if(btnCloseFeedModal) btnCloseFeedModal.addEventListener('click', closeFeedModal);
    if(feedModalOverlay) {
        feedModalOverlay.addEventListener('click', (e) => {
            if (e.target === feedModalOverlay) closeFeedModal(); // click outside
        });
    }

    // --- FAB Logic ---
    if(btnScrollTop) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 200) {
                btnScrollTop.classList.remove('opacity-0', 'translate-y-10', 'pointer-events-none');
            } else {
                btnScrollTop.classList.add('opacity-0', 'translate-y-10', 'pointer-events-none');
            }
        });
        
        btnScrollTop.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
    
    // --- Animal Sequence Logic ---
    function renderTags() {
        tagsContainer.innerHTML = '';
        pastAnimalsList.forEach((animal, index) => {
            const tag = document.createElement('div');
            tag.className = 'flex items-center gap-1 bg-dark-700 border border-dark-600 px-2 py-1 rounded text-xs text-brand-glow font-bold animate-fade-in';
            tag.innerHTML = `
                <span>${animal}</span>
                <button type="button" class="text-gray-400 hover:text-red-400 transition-colors ml-1" data-index="${index}">
                    <i class="fa-solid fa-times"></i>
                </button>
            `;
            tagsContainer.appendChild(tag);
        });
        
        // Add remove events
        tagsContainer.querySelectorAll('button').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const idx = parseInt(e.currentTarget.getAttribute('data-index'));
                pastAnimalsList.splice(idx, 1);
                renderTags();
            });
        });
    }

    if (btnAddAnimal) {
        btnAddAnimal.addEventListener('click', () => {
            const animalVal = selectAnimalSeq.value;
            const timeVal = selectTimeSeq.value;
            
            if (animalVal) {
                const combined = `${timeVal} - ${animalVal}`;
                pastAnimalsList.push(combined);
                renderTags();
                selectAnimalSeq.selectedIndex = 0; // reset
            }
        });
    }

    // --- Live Market Feed (Scraper) ---
    const fetchLiveFeed = async () => {
        if(!feedList) return;
        
        feedList.innerHTML = `<div class="p-4 flex items-center justify-center text-sm text-brand-prime"><i class="fa-solid fa-spinner fa-spin mr-2"></i> Escaneando satélite...</div>`;
        if(btnRefreshFeed) btnRefreshFeed.classList.add('animate-spin');

        try {
            const res = await fetch('/api/today-results');
            const data = await res.json();

            feedList.innerHTML = '';
            
            if (!data || Object.keys(data).length === 0) {
                feedList.innerHTML = `<div class="p-4 text-center text-sm text-gray-500 italic">No hay resultados oficiales hoy todavía.</div>`;
                return;
            }
            
            let htmlAccumulator = '';
            
            for (const [lotteryName, results] of Object.entries(data)) {
                htmlAccumulator += `
                <div class="mb-4">
                    <div class="bg-gray-100 text-gray-800 text-xs font-bold uppercase py-1 px-3 border-y border-gray-200 sticky top-0 z-10 shadow-sm flex items-center gap-2">
                        <i class="fa-solid fa-ranking-star text-brand-prime"></i> ${lotteryName}
                    </div>
                    <div class="divide-y divide-gray-100">
                `;
                
                if (!results || results.length === 0) {
                    htmlAccumulator += `<div class="p-3 text-center text-xs text-gray-400">Sin datos aún</div>`;
                } else {
                    results.forEach((item, index) => {
                        const delay = index * 30; // Faster cascade
                        htmlAccumulator += `
                        <div class="p-2 flex items-center justify-between text-sm animate-[fadeIn_0.5s_ease-out_forwards] hover:bg-gray-50 transition-colors" style="animation-delay: ${delay}ms; opacity: 0;">
                            <span class="text-gray-500 font-mono text-xs w-16">${item.schedule.replace(/ AM| PM/g, '')} <span class="text-[0.6rem] text-gray-400">${item.schedule.slice(-2)}</span></span>
                            <div class="flex items-center gap-2 flex-grow justify-end">
                                <span class="text-lg font-black text-gray-900 w-6 text-center">${item.animal.split(' ')[0]}</span>
                                <span class="text-sm font-bold text-brand-prime tracking-wide uppercase">${item.animal.substring(item.animal.indexOf(' ') + 1)}</span>
                            </div>
                        </div>
                        `;
                    });
                }
                htmlAccumulator += `</div></div>`;
            }
            
            feedList.innerHTML = htmlAccumulator;

        } catch(e) {
            console.error('Error fetching live feed', e);
            feedList.innerHTML = `<div class="p-4 flex items-center justify-center text-sm text-red-400"><i class="fa-solid fa-triangle-exclamation mr-2"></i> Error de conexión</div>`;
        } finally {
            if(btnRefreshFeed) {
                setTimeout(() => btnRefreshFeed.classList.remove('animate-spin'), 500);
            }
        }
    };

    if (btnRefreshFeed) {
        btnRefreshFeed.addEventListener('click', fetchLiveFeed);
        fetchLiveFeed();
    }

    // --- AI Engine Integration ---
    if (btnGenerateAI) {
        btnGenerateAI.addEventListener('click', async () => {
            const dateVal = inputDate.value.trim();
            const dreamVal = inputDream.value.trim();
            const analystName = 'LOTTO-ANY';
            const playType = selectPlayType.value;
            const targetLottery = (playType === 'Quiniela') ? 'Todas (Multi-Lotería)' : (selectLottery ? selectLottery.value : 'Lotto Activo');
            
            if(!dateVal || isNaN(dateVal) || dateVal.length < 4) {
                 alert('Por favor, ingresa una fecha base numérica válida (ej. 13032026).');
                 return;
            }
            
            // 1. Calculate underlying Pyramid internally (no UI)
            let hot_numbers = [];
            try {
                 const pyrRes = await fetch('/api/pyramid', {
                     method: 'POST',
                     headers: { 'Content-Type': 'application/json' },
                     body: JSON.stringify({ number: dateVal })
                 });
                 const pData = await pyrRes.json();
                 if(pData.hot_numbers) hot_numbers = pData.hot_numbers;
            } catch(e) {}
            
            // Setup UI State
            uiPlayTypeLabel.textContent = playType;
            btnGenerateAI.disabled = true;
            btnAIText.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-2"></i> Inicializando Nodos AI-ASR Core...';
            aiIdleState.style.opacity = '0';
            
            setTimeout(() => {
                 aiIdleState.classList.add('hidden');
                 aiHeader.classList.remove('hidden');
                 aiBody.classList.remove('hidden');
                 aiHeader.classList.add('flex');
                 
                 aiDynamicCards.innerHTML = ''; // Clear prev
                 eReasoning.innerHTML = '';
            }, 500);
            
            // Request Advanced AI Prediction
            const payload = {
                 analyst_name: analystName,
                 hot_numbers: hot_numbers,
                 past_animals: pastAnimalsList,
                 play_type: playType,
                 target_lottery: targetLottery,
                 dream: dreamVal
            };
            
            try {
                 const res = await fetch('/api/advanced-prediction', {
                     method: 'POST',
                     headers: { 'Content-Type': 'application/json' },
                     body: JSON.stringify(payload)
                 });
                 const data = await res.json();
                 
                 // Render Dynamic Cards
                 let htmlCards = '';
                 
                 // Helper to generate mini-animal chips inside a card
                 const generateChips = (combinations) => {
                     return combinations.map(c => `
                         <div class="flex items-center gap-2 bg-gray-50 border border-gray-200 rounded px-3 py-1 mb-1 shadow-sm">
                            <span class="text-xl font-black text-gray-800">${c.number}</span>
                            <span class="text-xs font-bold text-gray-500 tracking-wider">${c.animal}</span>
                         </div>
                     `).join('');
                 };

                 // 1. Primary Play Card
                 if(data.primary_play) {
                     const probFloat = parseFloat(data.primary_play.probability) || 0;
                     htmlCards += `
                        <div class="md:col-span-1 bg-gradient-to-b from-brand-prime/10 to-transparent border border-gray-200 rounded-xl p-4 flex flex-col items-center justify-start text-center relative overflow-hidden group">
                            <div class="absolute inset-x-0 -top-2 h-4 bg-brand-prime blur-xl opacity-20"></div>
                            <span class="text-[0.65rem] font-bold text-brand-prime tracking-widest uppercase mb-3">Target Principal</span>
                            
                            <div class="w-full flex inset-wrap flex-col gap-1 items-center justify-center flex-grow">
                                ${generateChips(data.primary_play.combination || [])}
                            </div>

                            <div class="mt-4 w-full bg-gray-200 rounded-full h-1.5 overflow-hidden">
                                <div class="bg-brand-prime h-full rounded-full transition-all duration-1000" style="width: ${probFloat}%"></div>
                            </div>
                            <span class="text-[0.65rem] text-gray-500 font-mono mt-1 w-full text-right">${data.primary_play.probability || '0%'} PROB.</span>
                        </div>
                     `;
                 }

                 // 2. Secondary Plays
                 if(data.secondary_plays && Array.isArray(data.secondary_plays)) {
                     const secondaryGrid = data.secondary_plays.map((sp, idx) => {
                         const probFloat = parseFloat(sp.probability) || 0;
                         return `
                         <div class="bg-gray-50 border border-gray-200 rounded-xl p-4 flex flex-col items-center justify-start text-center hover:border-brand-prime transition-colors">
                            <span class="text-[0.65rem] font-bold text-gray-400 tracking-widest uppercase mb-3">Respaldo ${idx + 1}</span>
                            
                            <div class="w-full flex inset-wrap flex-col gap-1 items-center justify-center flex-grow">
                                ${generateChips(sp.combination || [])}
                            </div>

                            <div class="mt-auto pt-4 w-full">
                                <div class="w-full bg-gray-200 rounded-full h-1 overflow-hidden">
                                    <div class="bg-gray-400 h-full rounded-full transition-all duration-1000" style="width: ${probFloat}%"></div>
                                </div>
                                <span class="text-[0.65rem] text-gray-500 font-mono mt-1">${sp.probability || '0%'}</span>
                            </div>
                        </div>
                         `;
                     }).join('');
                     
                     htmlCards += `
                        <div class="md:col-span-2 grid grid-cols-1 sm:grid-cols-2 gap-4">
                            ${secondaryGrid}
                        </div>
                     `;
                 }
                 
                 aiDynamicCards.innerHTML = htmlCards;

                 // Typewriter effect for Reasoning
                 const textToType = data.reasoning || "Análisis completado mediante reducción de series numéricas.";
                 let i = 0;
                 function typeWriter() {
                     if (i < textToType.length) {
                         eReasoning.innerHTML += textToType.charAt(i);
                         i++;
                         setTimeout(typeWriter, 15); // Speed of typing
                     }
                 }
                 typeWriter();
                 
            } catch(e) {
                 console.error(e);
                 alert('Error conectando con la API externa de IA. Posible interrupción en la red o formato de respuesta inválido.');
                 aiHeader.classList.add('hidden');
                 aiBody.classList.add('hidden');
                 aiIdleState.classList.remove('hidden');
                 aiIdleState.style.opacity = '1';
            } finally {
                 btnGenerateAI.disabled = false;
                 btnAIText.innerHTML = '<i class="fa-solid fa-microchip mr-2"></i> Analizar (AI-ASR)';
            }
        });
    }

    // --- Mini Random Simulator ---
    if (btnRandom) {
        btnRandom.addEventListener('click', async () => {
            btnRandom.classList.add('animate-spin');
            try {
                 const res = await fetch('/api/random?count=3');
                 const data = await res.json();
                 
                 randomResult.innerHTML = '';
                 data.forEach(item => {
                      const card = document.createElement('div');
                      card.className = 'random-card-mini';
                      card.innerHTML = `
                          <span class="num">${item.number}</span>
                          <span class="name">${item.animal.substring(0, 5)}</span>
                      `;
                      randomResult.appendChild(card);
                 });
            } catch(e) {}
            finally {
                 setTimeout(() => btnRandom.classList.remove('animate-spin'), 300);
            }
        });
        
        btnRandom.click();
    }
});
