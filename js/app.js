
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
window.els = {
    billAmount: document.getElementById('bill-amount'),
    homeCurrency: document.getElementById('home-currency'),
    billCurrencyRadios: document.getElementsByName('bill_currency'),

    // Toggles
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

// Optimization: Cache number formatters to avoid re-creating them on every render
const numberFormatters = {};
const getFormatter = (currency) => {
    if (!numberFormatters[currency]) {
        numberFormatters[currency] = new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: currency
        });
    }
    return numberFormatters[currency];
};

const FLAGS = {
    GBP: '🇬🇧', USD: '🇺🇸', EUR: '🇪🇺', AUD: '🇦🇺', CAD: '🇨🇦',
    TWD: '🇹🇼', JPY: '🇯🇵', CNY: '🇨🇳', RUB: '🇷🇺'
};
const SYMBOLS = {
    GBP: '£', USD: '$', EUR: '€', AUD: '$', CAD: '$', BOB: 'Bs',
    TWD: 'NT$', JPY: '¥', CNY: '¥', RUB: '₽'
};

// Initialization
async function init() {
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
    const updateBtn = (active, btn, checkIcon, mainIcon, colorClass, textClass) => {
        if(!btn) return;
        btn.setAttribute('aria-pressed', active);
        if(active) {
            btn.className = `w-full p-4 rounded-lg border-2 transition-all duration-200 flex items-center gap-3 bg-${colorClass}-50 dark:bg-${colorClass}-900/20 border-${colorClass}-500`;
            checkIcon.className = `w-5 h-5 rounded border-2 flex items-center justify-center bg-${colorClass}-500 border-${colorClass}-500 text-white`;
            checkIcon.innerHTML = '<span class="material-symbols-outlined text-[14px] font-bold">check</span>';
            mainIcon.className = `material-symbols-outlined ${textClass}`;
        } else {
             btn.className = `w-full p-4 rounded-lg border-2 transition-all duration-200 flex items-center gap-3 bg-white dark:bg-card-dark border-slate-200 dark:border-slate-700 hover:border-slate-300`;
             checkIcon.className = `w-5 h-5 rounded border-2 flex items-center justify-center border-slate-300`;
             checkIcon.innerHTML = '';
             mainIcon.className = `material-symbols-outlined text-slate-400`;
        }
    };

    updateBtn(state.hasUsdCash, els.btnToggleCash, els.iconCheckCash, els.iconCash, 'blue', 'text-blue-600');
    updateBtn(state.hasMoneyApp, els.btnToggleApp, els.iconCheckApp, els.iconApp, 'purple', 'text-purple-600');
    updateBtn(state.hasCard, els.btnToggleCard, els.iconCheckCard, els.iconCard, 'green', 'text-green-600');

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
    if (data.official_rates && data.official_rates['USD']) {
        const official = data.official_rates;

        // official_rates are based on USD (1 USD = X Currency)
        const usdToHome = official[state.homeCurrency];
        const usdToBob = official['BOB'];

        if (usdToHome && usdToBob) {
            // We want 1 Home = X USD.
            // If 1 USD = 0.82 GBP, then 1 GBP = 1/0.82 USD = 1.21 USD.
            state.rates.USD = 1 / usdToHome;
            state.rates.BOB = usdToBob / usdToHome;
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
    if (data.date && els.lastUpdated) {
         els.lastUpdated.innerHTML = `
            <span class="material-symbols-outlined text-[14px]">update</span>
            <span>Updated: ${data.date}</span>
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

    // Helper to format money (optimized)
    const fmt = (n) => getFormatter(cur).format(n);

    // 1. Render Winner Card
    els.winnerCardContainer.innerHTML = `
        <div class="relative overflow-hidden rounded-2xl bg-gradient-to-br from-green-500 to-emerald-600 p-6 shadow-lg shadow-green-500/20 text-white">
            <div class="absolute -right-10 -top-10 h-32 w-32 rounded-full bg-white/10 blur-2xl"></div>
            <div class="absolute -left-10 -bottom-10 h-32 w-32 rounded-full bg-black/10 blur-2xl"></div>
            <div class="relative z-10">
                <div class="flex items-center justify-between mb-4">
                    <div class="flex items-center gap-2 rounded-full bg-white/20 px-3 py-1 backdrop-blur-sm">
                        <span class="material-symbols-outlined text-sm">emoji_events</span>
                        <span class="text-xs font-bold uppercase tracking-wide">Cheapest Option</span>
                    </div>
                    <span class="material-symbols-outlined opacity-50">${getIcon(best.type)}</span>
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
                        <span class="material-symbols-outlined">${getIcon(res.type)}</span>
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
                    <span class="material-symbols-outlined text-lg">savings</span>
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
init();
