
// Defaults
const DEFAULTS = {
    homeCurrency: 'GBP',
    billAmount: 0,
    billCurrency: 'BOB', // 'BOB' or 'USD'

    // Payment Methods
    hasUsdCash: true,
    hasMoneyApp: true,
    hasCard: true,

    // Street Cash Params
    streetExchangeRate: 7.85, // Default backup

    // Money App Params
    appFee: 1.99,

    // Card Params
    bankFeePct: 0.0,
    merchantUsdRate: 6.96
};

const ICON_PATHS = {
    "flag": "M200-120v-680h343l19 86h238v370H544l-18.93-85H260v309h-60Zm300-452Zm95 168h145v-250H511l-19-86H260v251h316l19 85Z",
    "attach_money": "M451-120v-84q-57-10-93.5-43.5T305-332l56-23q17 48 49 71.5t77 23.5q48 0 79-24t31-66q0-44-27.5-68T466-467q-72-23-107.5-61T323-623q0-55 35.5-92t92.5-42v-83h60v83q45 5 77.5 29.5T638-665l-56 24q-14-32-37.5-46.5T483-702q-46 0-73 21t-27 57q0 38 30 61.5T524-514q68 21 100.5 60.5T657-354q0 63-37 101.5T511-203v83h-60Z",
    "payments": "M540-420q-50 0-85-35t-35-85q0-50 35-85t85-35q50 0 85 35t35 85q0 50-35 85t-85 35ZM220-280q-24.75 0-42.37-17.63Q160-315.25 160-340v-400q0-24.75 17.63-42.38Q195.25-800 220-800h640q24.75 0 42.38 17.62Q920-764.75 920-740v400q0 24.75-17.62 42.37Q884.75-280 860-280H220Zm100-60h440q0-42 29-71t71-29v-200q-42 0-71-29t-29-71H320q0 42-29 71t-71 29v200q42 0 71 29t29 71Zm480 180H100q-24.75 0-42.37-17.63Q40-195.25 40-220v-460h60v460h700v60ZM220-340v-400 400Z",
    "smartphone": "M260-40q-24.75 0-42.37-17.63Q200-75.25 200-100v-760q0-24 18-42t42-18h438q24.75 0 42.38 17.62Q758-884.75 758-860v150q18 3 30 16.95 12 13.96 12 31.63V-587q0 19-12 33t-30 17v437q0 24.75-17.62 42.37Q722.75-40 698-40H260Zm0-60h438v-760H260v760Zm0 0v-760 760Zm219-620q12 0 21-9t9-21q0-12-9-21t-21-9q-12 0-21 9t-9 21q0 12 9 21t21 9Z",
    "credit_card": "M880-740v520q0 24-18 42t-42 18H140q-24 0-42-18t-18-42v-520q0-24 18-42t42-18h680q24 0 42 18t18 42ZM140-631h680v-109H140v109Zm0 129v282h680v-282H140Zm0 282v-520 520Z",
    "expand_more": "M480-344 240-584l43-43 197 197 197-197 43 43-240 240Z",
    "update": "M483-120q-75 0-141-28.5T226.5-226q-49.5-49-78-115T120-482q0-75 28.5-140t78-113.5Q276-784 342-812t141-28q80 0 151.5 35T758-709v-106h60v208H609v-60h105q-44-51-103.5-82T483-780q-125 0-214 85.5T180-485q0 127 88 216t215 89q125 0 211-88t86-213h60q0 150-104 255.5T483-120Zm122-197L451-469v-214h60v189l137 134-43 43Z",
    "local_atm": "M453-274h60v-45h48q15 0 24.5-12t9.5-27v-114.74q0-16.26-9.5-27.76T561-512H425v-69h170v-60h-82v-45h-60v45h-49q-15 0-27 12t-12 28.12v113.76q0 16.12 12 25.62t27 9.5h131v73H365v60h88v45ZM140-160q-24 0-42-18t-18-42v-520q0-24 18-42t42-18h680q24 0 42 18t18 42v520q0 24-18 42t-42 18H140Zm0-60h680v-520H140v520Zm0 0v-520 520Z",
    "account_balance": "M212-241v-339h60v339h-60Zm242 0v-339h60v339h-60ZM80-121v-60h800v60H80Zm608-120v-339h60v339h-60ZM80-640v-53l400-228 400 228v53H80Zm134-60h532-532Zm0 0h532L480-852 214-700Z",
    "currency_exchange": "M480-40q-112 0-216-66T100-257v137H40v-240h240v60H143q51 77 145.5 138.5T480-100q78 0 147.5-30t121-81.5Q800-263 830-332.5T860-480h60q0 91-34.5 171T791-169q-60 60-140 94.5T480-40Zm-29-153v-54q-45-12-75.5-38.5T324-358l51-17q12 38 42.5 60t69.5 22q40 0 66.5-19.5T580-364q0-33-25-55.5T463-470q-60-25-90-54t-30-78q0-44 30-75t80-38v-51h55v51q38 4 66 24t45 55l-48 23q-15-28-37-42t-52-14q-39 0-61.5 18T398-602q0 32 26 51t84 43q69 29 98 61t29 83q0 25-9 46t-25.5 36Q584-267 560-257.5T506-245v52h-55ZM40-480q0-91 34.5-171T169-791q60-60 140-94.5T480-920q112 0 216 66t164 151v-137h60v240H680v-60h137q-51-77-145-138.5T480-860q-78 0-147.5 30t-121 81.5Q160-697 130-627.5T100-480H40Z",
    "calculate": "M314-228h50v-88h88v-50h-88v-88h-50v88h-88v50h88v88Zm215-35h201v-49H529v49Zm0-107h201v-50H529v50Zm37-163 61-61 61 61 36-36-61-61 61-61-36-36-61 61-61-61-36 36 61 61-61 61 36 36Zm-325-72h196v-50H241v50Zm-61 485q-24 0-42-18t-18-42v-600q0-24 18-42t42-18h600q24 0 42 18t18 42v600q0 24-18 42t-42 18H180Zm0-60h600v-600H180v600Zm0-600v600-600Z",
    "open_in_new": "M180-120q-24 0-42-18t-18-42v-600q0-24 18-42t42-18h279v60H180v600h600v-279h60v279q0 24-18 42t-42 18H180Zm202-219-42-43 398-398H519v-60h321v321h-60v-218L382-339Z",
    "check": "M378-246 154-470l43-43 181 181 384-384 43 43-427 427Z",
    "emoji_events": "M298-120v-60h152v-148q-54-11-96-46.5T296-463q-74-8-125-60t-51-125v-44q0-25 17.5-42.5T180-752h104v-88h392v88h104q25 0 42.5 17.5T840-692v44q0 73-51 125t-125 60q-16 53-58 88.5T510-328v148h152v60H298Zm-14-406v-166H180v44q0 45 29.5 78.5T284-526Zm196 141q57 0 96.5-40t39.5-97v-258H344v258q0 57 39.5 97t96.5 40Zm196-141q45-10 74.5-43.5T780-648v-44H676v166Zm-196-57Z",
    "savings": "M640-520q17 0 28.5-11.5T680-560q0-17-11.5-28.5T640-600q-17 0-28.5 11.5T600-560q0 17 11.5 28.5T640-520ZM320-620h200v-60H320v60ZM180-120q-34-114-67-227.5T80-580q0-92 64-156t156-64h200q29-38 70.5-59t89.5-21q25 0 42.5 17.5T720-820q0 6-1.5 12t-3.5 11q-4 11-7.5 22.5T702-751l91 91h87v279l-113 37-67 224H480v-80h-80v80H180Zm45-60h115v-80h200v80h115l63-210 102-35v-175h-52L640-728q1-25 6.5-48.5T658-824q-38 10-72 29.5T534-740H300q-66.29 0-113.14 46.86Q140-646.29 140-580q0 103.16 29 201.58Q198-280 225-180Zm255-322Z"
};

const COLOR_MAP = {
    cash: { bg: 'bg-blue-50', bgDark: 'dark:bg-blue-900/20', border: 'border-blue-500', bgSolid: 'bg-blue-500', text: 'text-blue-600' },
    app: { bg: 'bg-purple-50', bgDark: 'dark:bg-purple-900/20', border: 'border-purple-500', bgSolid: 'bg-purple-500', text: 'text-purple-600' },
    card: { bg: 'bg-green-50', bgDark: 'dark:bg-green-900/20', border: 'border-green-500', bgSolid: 'bg-green-500', text: 'text-green-600' }
};

function getIconSvg(name, classes = "w-6 h-6") {
    if (!ICON_PATHS[name]) return '';
    return `<svg class="${classes}" fill="currentColor" viewBox="0 -960 960 960" xmlns="http://www.w3.org/2000/svg"><path d="${ICON_PATHS[name]}"/></svg>`;
}

// State
let state = {
    ...DEFAULTS,
    rates: {
        USD: 0,
        BOB: 0
    },
    homeToUsdRate: 0, // Changed from usdHomeBuyRate
    appRate: 0,
    cardBobRate: 0, // New rate for Card (BOB)
    lastUpdated: null
};

// Elements
window.els = {};

function initEls() {
    window.els = {
        billAmount: document.getElementById('bill-amount'),
        homeCurrency: document.getElementById('home-currency'),
        billCurrencyRadios: document.getElementsByName('bill_currency'),

        // Toggles
        themeToggle: document.getElementById('theme-toggle'),
        btnToggleCash: document.getElementById('btn-toggle-cash'),
        btnToggleApp: document.getElementById('btn-toggle-app'),
        btnToggleCard: document.getElementById('btn-toggle-card'),
        iconCheckCash: document.getElementById('icon-check-cash'),
        iconCheckApp: document.getElementById('icon-check-app'),
        iconCheckCard: document.getElementById('icon-check-card'),
        iconCash: document.getElementById('icon-cash'),
        iconApp: document.getElementById('icon-app'),
        iconCard: document.getElementById('icon-card'),

        // Rate Containers
        ratesContainerCash: document.getElementById('rates-container-cash'),
        ratesContainerApp: document.getElementById('rates-container-app'),
        ratesContainerCard: document.getElementById('rates-container-card'),

        // Inputs
        homeToUsdRate: document.getElementById('home-to-usd-rate'),
        streetExchangeRate: document.getElementById('street-exchange-rate'),
        appRate: document.getElementById('app-rate'),
        appFee: document.getElementById('app-fee'),
        bankFeePct: document.getElementById('bank-fee-pct'),
        bankFeeNumber: document.getElementById('bank-fee-number'),
        cardBobRate: document.getElementById('card-bob-rate'),
        merchantUsdRate: document.getElementById('merchant-usd-rate'),

        // Containers
        winnerCardContainer: document.getElementById('winner-card-container'),
        resultsList: document.getElementById('results-list'),
        savingsAlertContainer: document.getElementById('savings-alert-container'),
        lastUpdated: document.getElementById('last-updated'),

        // Display
        flagIcon: document.getElementById('flag-icon'),
        currencySymbol: document.getElementById('currency-symbol'),
        homeCurrencyCodeDisplay: document.getElementById('home-currency-code-display'),
        appFeeCurrency: document.getElementById('app-fee-currency'),
        bankFeeDisplay: document.getElementById('bank-fee-display'),

        // Dynamic Labels
        labelHomeUsd: document.getElementById('label-home-to-usd'),
        labelAppRate: document.getElementById('label-app-rate'),
        labelOfficialRate: document.getElementById('label-official-rate')
    };
}

const FLAGS = {
    GBP: '🇬🇧', USD: '🇺🇸', EUR: '🇪🇺', AUD: '🇦🇺', CAD: '🇨🇦',
    TWD: '🇹🇼', JPY: '🇯🇵', CNY: '🇨🇳', RUB: '🇷🇺',
    NZD: '🇳🇿', SEK: '🇸🇪', NOK: '🇳🇴', DKK: '🇩🇰', CHF: '🇨🇭',
    KRW: '🇰🇷', ILS: '🇮🇱'
};
const SYMBOLS = {
    GBP: '£', USD: '$', EUR: '€', AUD: '$', CAD: '$', BOB: 'Bs',
    TWD: 'NT$', JPY: '¥', CNY: '¥', RUB: '₽',
    NZD: '$', SEK: 'kr', NOK: 'kr', DKK: 'kr', CHF: 'Fr.',
    KRW: '₩', ILS: '₪'
};

// Initialization
async function init() {
    initEls();
    initTheme();
    initCurrency();
    setupEventListeners();
    updateToggleUI(); // Initialize UI state

    // Try to load from cache first for instant UI
    if (loadCachedRates()) {
        populateInputs();
        updateCurrencyDisplay();
        calculate();
    }

    await fetchRates();
    populateInputs();
    updateCurrencyDisplay();
    calculate();
}

function initTheme() {
    const theme = localStorage.getItem('theme');
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const systemDark = mediaQuery.matches;
    const isDark = theme === 'dark' || (!theme && systemDark);

    // Initial Set
    if (isDark) {
        document.documentElement.classList.add('dark');
        if(els.themeToggle) els.themeToggle.checked = true;
    } else {
        document.documentElement.classList.remove('dark');
        if(els.themeToggle) els.themeToggle.checked = false;
    }

    // Toggle Listener
    if(els.themeToggle) {
        els.themeToggle.addEventListener('change', (e) => {
            if (e.target.checked) {
                document.documentElement.classList.add('dark');
                localStorage.setItem('theme', 'dark');
            } else {
                document.documentElement.classList.remove('dark');
                localStorage.setItem('theme', 'light');
            }
        });
    }

    // System Preference Listener
    mediaQuery.addEventListener('change', (e) => {
        if (!localStorage.getItem('theme')) {
            if (e.matches) {
                document.documentElement.classList.add('dark');
                if(els.themeToggle) els.themeToggle.checked = true;
            } else {
                document.documentElement.classList.remove('dark');
                if(els.themeToggle) els.themeToggle.checked = false;
            }
        }
    });
}

function initCurrency() {
    const stored = localStorage.getItem('homeCurrency');
    if (stored && FLAGS[stored]) {
        state.homeCurrency = stored;
        if(els.homeCurrency) els.homeCurrency.value = stored;
    }
}

function setupEventListeners() {
    // Bill Amount
    els.billAmount.addEventListener('input', (e) => {
        state.billAmount = parseFloat(e.target.value) || 0;
        debouncedCalculate();
    });

    // Bill Currency Toggle
    els.billCurrencyRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            if(e.target.checked) {
                state.billCurrency = e.target.value;
                updateCurrencyDisplay();
                calculate();
            }
        });
    });

    // Home Currency
    els.homeCurrency.addEventListener('change', async (e) => {
        state.homeCurrency = e.target.value;
        localStorage.setItem('homeCurrency', state.homeCurrency);
        updateCurrencyDisplay();
        await fetchRates(); // Fetch new rates for the new base
        populateInputs();
        calculate();
    });

    // Payment Method Toggles
    const toggleMethod = (key, btn) => {
        if(!btn) return;
        btn.addEventListener('click', () => {
            state[key] = !state[key];
            updateToggleUI();
            calculate();
        });
    };

    toggleMethod('hasUsdCash', els.btnToggleCash);
    toggleMethod('hasMoneyApp', els.btnToggleApp);
    toggleMethod('hasCard', els.btnToggleCard);

    // Input Listeners
    const linkInput = (el, key) => {
        if (!el) return;
        el.addEventListener('input', (e) => {
            state[key] = parseFloat(e.target.value) || 0;
            debouncedCalculate();
        });
    };

    linkInput(els.homeToUsdRate, 'homeToUsdRate');
    linkInput(els.streetExchangeRate, 'streetExchangeRate');
    linkInput(els.appRate, 'appRate');
    linkInput(els.appFee, 'appFee');
    linkInput(els.bankFeePct, 'bankFeePct');
    linkInput(els.cardBobRate, 'cardBobRate');
    linkInput(els.merchantUsdRate, 'merchantUsdRate');

    // Special listener for Bank Fee display
    if(els.bankFeePct) {
        els.bankFeePct.addEventListener('input', (e) => {
             const val = parseFloat(e.target.value);
             if(els.bankFeeDisplay) els.bankFeeDisplay.textContent = val + '%';
             if(els.bankFeeNumber) els.bankFeeNumber.value = val;
             state.bankFeePct = val; // Ensure state updates too
             debouncedCalculate();
        });
    }

    if(els.bankFeeNumber) {
        els.bankFeeNumber.addEventListener('input', (e) => {
            let val = parseFloat(e.target.value) || 0;
            // Clamp value
            if (val < 0) val = 0;
            if (val > 5) val = 5;

            state.bankFeePct = val;
            if(els.bankFeePct) els.bankFeePct.value = val;
            if(els.bankFeeDisplay) els.bankFeeDisplay.textContent = val + '%';
            debouncedCalculate();
        });
    }
}

function updateToggleUI() {
    const updateBtn = (active, btn, checkIcon, mainIcon, type) => {
        if(!btn) return;
        const colors = COLOR_MAP[type];
        btn.setAttribute('aria-pressed', active);
        if(active) {
            btn.className = `w-full p-4 rounded-lg border-2 transition-all duration-200 flex items-center gap-3 ${colors.bg} ${colors.bgDark} ${colors.border}`;
            checkIcon.className = `w-5 h-5 rounded border-2 flex items-center justify-center ${colors.bgSolid} ${colors.border} text-white`;
            checkIcon.innerHTML = getIconSvg('check', 'w-[14px] h-[14px]');
            mainIcon.setAttribute('class', `${colors.text} w-6 h-6`);
        } else {
             btn.className = `w-full p-4 rounded-lg border-2 transition-all duration-200 flex items-center gap-3 bg-white dark:bg-card-dark border-slate-200 dark:border-slate-700 hover:border-slate-300`;
             checkIcon.className = `w-5 h-5 rounded border-2 flex items-center justify-center border-slate-300`;
             checkIcon.innerHTML = '';
             mainIcon.setAttribute('class', `text-slate-400 w-6 h-6`);
        }
    };

    updateBtn(state.hasUsdCash, els.btnToggleCash, els.iconCheckCash, els.iconCash, 'cash');
    updateBtn(state.hasMoneyApp, els.btnToggleApp, els.iconCheckApp, els.iconApp, 'app');
    updateBtn(state.hasCard, els.btnToggleCard, els.iconCheckCard, els.iconCard, 'card');

    // Show/Hide Containers
    const toggleContainer = (container, visible) => {
        if (!container) return;
        if (visible) {
            container.classList.remove('max-h-0', 'opacity-0', 'mt-0');
            container.classList.add('max-h-[500px]', 'opacity-100', 'mt-4');
        } else {
            container.classList.remove('max-h-[500px]', 'opacity-100', 'mt-4');
            container.classList.add('max-h-0', 'opacity-0', 'mt-0');
        }
    };

    toggleContainer(els.ratesContainerCash, state.hasUsdCash);
    toggleContainer(els.ratesContainerApp, state.hasMoneyApp);
    toggleContainer(els.ratesContainerCard, state.hasCard);
}

function updateCurrencyDisplay() {
    // Update Flag
    els.flagIcon.textContent = FLAGS[state.homeCurrency] || '🌍';

    // Update Bill Currency Symbol
    els.currencySymbol.textContent = SYMBOLS[state.billCurrency] || '$';

    // Update Home Currency Code in Inputs label
    if (els.homeCurrencyCodeDisplay) {
        els.homeCurrencyCodeDisplay.textContent = state.homeCurrency;
    }

    // Update App Fee Currency
    if (els.appFeeCurrency) {
        els.appFeeCurrency.textContent = SYMBOLS[state.homeCurrency] || '';
    }

    // Update Dynamic Labels
    if (els.labelHomeUsd) {
        els.labelHomeUsd.textContent = `How much USD can ${SYMBOLS[state.homeCurrency] || state.homeCurrency}1 buy`;
    }
    if (els.labelAppRate) {
        els.labelAppRate.textContent = `Transfer App ${state.homeCurrency} → BOB`;
    }
    if (els.labelOfficialRate) {
        els.labelOfficialRate.textContent = `Official Rate (${state.homeCurrency} → BOB)`;
    }
}

// Data Fetching
function processRatesData(data) {
    // 1. Process Official Rates
    // Supports both old USD-base (implicit 1) and new GBP-base
    if (data.official_rates) {
        const official = data.official_rates;

        // Handle base currency transition
        // If data.base is set, use it. Otherwise assume USD.
        // But regardless of base, we need to convert everything relative to Home Currency.

        // Rate(Home->Target) = Rate(Base->Target) / Rate(Base->Home)

        const baseToHome = official[state.homeCurrency];
        const baseToBob = official['BOB'];
        const baseToUsd = official['USD'] || ((!data.base || data.base === 'USD') ? 1 : 0); // If base is USD or missing (legacy), USD is 1.

        if (baseToHome && baseToBob && baseToUsd) {
            // We want 1 Home = X USD.
            state.rates.USD = baseToUsd / baseToHome;
            // We want 1 Home = Y BOB.
            state.rates.BOB = baseToBob / baseToHome;
        }
    }

    // 2. Process Street Rate
    if (data.street_rate_bob && data.street_rate_bob > 0) {
        state.streetExchangeRate = data.street_rate_bob;
    }

    // Update derived defaults
    // rate is "USD per 1 Home"
    state.homeToUsdRate = state.rates.USD || 1;

    // App Rate: Defaults to blank (0)
    // Only reset if 0 (initial) so we don't overwrite user input if called multiple times?
    // Actually, fetchRates overwrote it every time. So we keep that behavior.
    state.appRate = 0;

    // Card BOB Rate (Home -> BOB).
    state.cardBobRate = state.rates.BOB || 1;

    // Update Last Updated Date
    if ((data.date || data.timestamp) && els.lastUpdated) {
        let dateStr = 'Unknown';
        try {
            let dateObj = null;
            // 1. Try timestamp
            if (data.timestamp) {
                dateObj = new Date(data.timestamp * 1000);
            }

            // 2. If invalid or missing, try date string
            if ((!dateObj || isNaN(dateObj.getTime())) && data.date) {
                dateObj = new Date(data.date);
                // 3. If still invalid, try cleaning date string (strip microseconds)
                if (isNaN(dateObj.getTime())) {
                    const fixedDate = data.date.replace(/(\.\d{3})\d+/, '$1');
                    dateObj = new Date(fixedDate);
                }
            }

            if (dateObj && !isNaN(dateObj.getTime())) {
                dateStr = dateObj.toLocaleString(undefined, {
                    year: 'numeric',
                    month: 'numeric',
                    day: 'numeric',
                    hour: 'numeric',
                    minute: 'numeric',
                    second: 'numeric',
                    timeZoneName: 'short',
                    hour12: false
                });
            } else {
                throw new Error("Invalid Date generated");
            }

        } catch (e) {
            console.error("Date parsing error", e);
            dateStr = data.date || 'Unknown';
        }

         els.lastUpdated.innerHTML = `
            ${getIconSvg('update', 'w-[14px] h-[14px]')}
            <span>Updated: ${dateStr}</span>
        `;
    }
}

function loadCachedRates() {
    const cached = localStorage.getItem('rates_cache');
    if (cached) {
        try {
            const data = JSON.parse(cached);
            console.log("Loaded rates from cache");
            processRatesData(data);
            return true;
        } catch (e) {
            console.error("Failed to parse cached rates", e);
            return false;
        }
    }
    return false;
}

async function fetchRates() {
    try {
        const res = await fetch('data/rates.json');
        const data = await res.json();

        // Cache the fresh data
        localStorage.setItem('rates_cache', JSON.stringify(data));

        processRatesData(data);
    } catch (e) {
        console.error("Fetch failed:", e);
    }
}

function populateInputs() {
    if(els.homeToUsdRate) els.homeToUsdRate.value = parseFloat(state.homeToUsdRate.toFixed(4));
    if(els.streetExchangeRate) els.streetExchangeRate.value = state.streetExchangeRate;
    if(els.appRate) {
        // Leave blank if 0
        els.appRate.value = (state.appRate > 0) ? parseFloat(state.appRate.toFixed(2)) : '';
    }
    if(els.appFee) els.appFee.value = state.appFee;
    if(els.bankFeePct) els.bankFeePct.value = state.bankFeePct;
    if(els.bankFeeNumber) els.bankFeeNumber.value = state.bankFeePct;
    if(els.bankFeeDisplay) els.bankFeeDisplay.textContent = state.bankFeePct + '%';
    if(els.cardBobRate) els.cardBobRate.value = parseFloat(state.cardBobRate.toFixed(2));
    if(els.merchantUsdRate) els.merchantUsdRate.value = state.merchantUsdRate;
}

function calculate() {
    const {
        hasUsdCash, hasMoneyApp, hasCard, // Added new state props
        billAmount, billCurrency,
        streetExchangeRate, homeToUsdRate,
        appRate, appFee,
        cardBobRate,
        bankFeePct, merchantUsdRate
    } = state;

    const results = [];

    // Option A: Paying with Cash (Street USD)
    if (hasUsdCash) {
        // You need USD.
        let usdNeededStreet = (billCurrency === 'BOB') ? (billAmount / streetExchangeRate) : billAmount;

        // Cost in Home = USD Needed / (USD per 1 Home)
        // Example: Need $100. Rate is 1.25 $/£. Cost = 100 / 1.25 = £80.
        let costStreet = 0;
        if (homeToUsdRate > 0) {
            costStreet = usdNeededStreet / homeToUsdRate;
        }

        results.push({
            id: 'cashStreet',
            type: 'cash',
            title: 'Street exchange',
            desc: `Exch: ${streetExchangeRate} BOB/$`,
            val: costStreet
        });
    }

    // Option B: Paying with Cash (Money App)
    if (hasMoneyApp) {
        let targetBOB = (billCurrency === 'BOB') ? billAmount : (billAmount * merchantUsdRate);
        let costApp = 0;
        if (appRate > 0) {
            costApp = (targetBOB / appRate) + appFee;
        }
        results.push({
            id: 'cashApp',
            type: 'app',
            title: 'Money Transfer App',
            desc: `Fee: ${SYMBOLS[state.homeCurrency]}${appFee}`,
            val: costApp
        });
    }

    // Option C & D: Paying with Card
    if (hasCard) {
        // Paying with Card (in BOB)
        let cardAmountBOB = (billCurrency === 'BOB') ? billAmount : (billAmount * merchantUsdRate);
        // Use the editable cardBobRate
        let costCardBob = 0;
        if (cardBobRate > 0) {
            costCardBob = (cardAmountBOB / cardBobRate) * (1 + (bankFeePct / 100));
        }
        results.push({
            id: 'cardBob',
            type: 'card',
            title: 'Card (in BOB)',
            desc: 'Bank Conversion',
            val: costCardBob
        });

        // Paying with Card (in USD)
        let terminalUsdCharge = (billCurrency === 'BOB') ? (billAmount / merchantUsdRate) : billAmount;
        // Bank charges you in Home currency for this USD amount.
        let costCardUsd = 0;
        if (homeToUsdRate > 0) {
            costCardUsd = (terminalUsdCharge / homeToUsdRate) * (1 + (bankFeePct / 100));
        }

        results.push({
            id: 'cardUsd',
            type: 'card',
            title: 'Card (in USD)',
            desc: 'Bank Conversion',
            val: costCardUsd
        });
    }

    updateUI(results);
}

function updateUI(results) {
    const cur = state.homeCurrency;

    // Filter valid and sort
    const validResults = results.filter(r => r.val > 0 && isFinite(r.val))
                                .sort((a, b) => a.val - b.val);

    if (validResults.length === 0) {
        els.winnerCardContainer.innerHTML = '';
        els.resultsList.innerHTML = '';
        els.savingsAlertContainer.innerHTML = '';
        return;
    }

    const best = validResults[0];
    const worst = validResults[validResults.length - 1];
    const savings = worst.val - best.val;

    // Helper to format money
    const fmt = (n) => n.toLocaleString('en-US', { style: 'currency', currency: cur });

    // 1. Render Winner Card
    els.winnerCardContainer.innerHTML = `
        <div class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-green-500 to-emerald-600 p-6 shadow-lg shadow-green-500/20 text-white">
            <div class="absolute -right-10 -top-10 h-32 w-32 rounded-full bg-white/10 blur-2xl"></div>
            <div class="absolute -left-10 -bottom-10 h-32 w-32 rounded-full bg-black/10 blur-2xl"></div>
            <div class="relative z-10">
                <div class="flex items-center justify-between mb-4">
                    <div class="flex items-center gap-2 rounded-full bg-white/20 px-3 py-1 backdrop-blur-sm">
                        ${getIconSvg('emoji_events', 'w-3.5 h-3.5')}
                        <span class="text-xs font-bold uppercase tracking-wide">Cheapest Option</span>
                    </div>
                    <div class="opacity-50">${getIconSvg(getIcon(best.type), 'w-6 h-6')}</div>
                </div>
                <div class="flex flex-col gap-1">
                    <h2 class="text-3xl font-bold tracking-tight">${fmt(best.val)}</h2>
                    <p class="text-green-50 font-medium">Using ${best.title}</p>
                </div>
            </div>
        </div>
    `;

    // 2. Render List
    els.resultsList.innerHTML = '';

    // Render the rest (skipping the winner)
    let listHTML = '';
    validResults.slice(1).forEach((res, index) => {
        const isWorst = (res === worst && validResults.length > 1);
        const diff = res.val - best.val;
        const diffPct = (diff / best.val) * 100;
        const diffPctStr = diffPct.toFixed(1) + '%';

        // Styling based on worst or normal
        let containerClasses, iconBg, textClass, diffTextClass, extraBadge;

        if (isWorst) {
            containerClasses = "flex items-center justify-between rounded-xl bg-card-light dark:bg-card-dark p-4 shadow-sm border border-danger/20 relative overflow-hidden";
            iconBg = "bg-danger/10 text-danger";
            textClass = "text-danger";
            diffTextClass = "text-danger/70";

            extraBadge = `
                <div class="absolute left-0 top-0 bottom-0 w-1 bg-danger"></div>
                <div class="flex items-center gap-1 mt-0.5">
                    <span class="rounded bg-danger/10 px-1.5 py-0.5 text-[10px] font-bold text-danger uppercase tracking-wider">Avoid</span>
                </div>
             `;
        } else {
            // Intermediate (Warning/Yellow)
            containerClasses = "flex items-center justify-between rounded-xl bg-card-light dark:bg-card-dark p-4 shadow-sm border border-warning/50 relative overflow-hidden";
            iconBg = "bg-warning/20 text-yellow-700";
            textClass = "text-yellow-900 dark:text-yellow-100";
            diffTextClass = "text-yellow-700 dark:text-yellow-200";

            extraBadge = `<p class="text-xs text-yellow-800/80 dark:text-yellow-200/80">${res.desc}</p>`;
        }

        listHTML += `
            <div class="${containerClasses}">
                <div class="flex items-center gap-3">
                    <div class="flex h-10 w-10 items-center justify-center rounded-full ${iconBg}">
                        ${getIconSvg(getIcon(res.type), 'w-6 h-6')}
                    </div>
                    <div>
                        <p class="text-sm font-bold text-slate-900 dark:text-white">${res.title}</p>
                        ${extraBadge}
                    </div>
                </div>
                <div class="text-right">
                    <p class="text-base font-bold ${textClass}">${fmt(res.val)}</p>
                    <span class="text-[10px] font-bold ${diffTextClass} uppercase">+${fmt(diff)} (+${diffPctStr})</span>
                </div>
            </div>
        `;
    });
    els.resultsList.innerHTML = listHTML;

    // 3. Render Savings Alert
    if (validResults.length > 1) {
        els.savingsAlertContainer.innerHTML = `
            <div class="flex items-center gap-3 rounded-xl bg-warning/20 p-4 border border-warning/30">
                <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-warning text-yellow-900">
                    ${getIconSvg('savings', 'w-5 h-5')}
                </div>
                <p class="text-sm font-medium text-yellow-900 dark:text-yellow-100">
                    You save <span class="font-bold">${fmt(savings)}</span> compared to paying directly with your card!
                </p>
            </div>
        `;
    } else {
        els.savingsAlertContainer.innerHTML = '';
    }
}

function getIcon(type) {
    switch(type) {
        case 'cash': return 'payments';
        case 'app': return 'smartphone';
        case 'card': return 'credit_card';
        default: return 'attach_money';
    }
}

function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

const debouncedCalculate = debounce(calculate, 300);

// Start
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}
