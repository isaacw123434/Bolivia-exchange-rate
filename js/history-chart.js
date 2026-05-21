// self-contained exchange rate snapshot sync & responsive SVG double line chart
document.addEventListener('DOMContentLoaded', () => {
    syncRatesSnapshot();
    initHistoryChart();
});

// 1. Sync rates snapshot at the top of the history page
function syncRatesSnapshot() {
    const elStreet = document.getElementById('today-street-rate');
    const elOfficial = document.getElementById('today-official-rate');
    const elDiff = document.getElementById('today-difference');
    const elUpdated = document.getElementById('today-updated');

    if (!elStreet) return;

    function updateDOM(data) {
        if (!data) return;
        const officialRates = data.official_rates || {};
        const streetRate = parseFloat(data.street_rate_bob || 0);
        const baseToUsd = parseFloat(officialRates.USD || 1);
        const baseToBob = parseFloat(officialRates.BOB || 0);
        const officialUsdBob = baseToUsd && baseToBob ? baseToBob / baseToUsd : 0;
        const streetPremium = officialUsdBob ? ((streetRate / officialUsdBob) - 1) * 100 : 0;

        if (streetRate) elStreet.textContent = `${streetRate.toFixed(2)} BOB`;
        if (officialUsdBob) elOfficial.textContent = `${officialUsdBob.toFixed(2)} BOB`;
        if (officialUsdBob) elDiff.textContent = `${streetPremium.toFixed(1)}%`;

        if (data.date || data.timestamp) {
            let dateStr = data.date || 'Unknown';
            try {
                let dateObj = null;
                if (data.timestamp) {
                    dateObj = new Date(data.timestamp * 1000);
                } else if (data.date) {
                    dateObj = new Date(data.date);
                    if (isNaN(dateObj.getTime())) {
                        dateObj = new Date(data.date.replace(/(\.\d{3})\d+/, '$1'));
                    }
                }
                if (dateObj && !isNaN(dateObj.getTime())) {
                    dateStr = dateObj.toLocaleString(undefined, {
                        year: 'numeric', month: 'numeric', day: 'numeric',
                        hour: 'numeric', minute: 'numeric', second: 'numeric',
                        timeZoneName: 'short', hour12: false
                    });
                }
            } catch(e) {}
            elUpdated.textContent = dateStr;
        }
    }

    // Try reading cached rates first
    try {
        const cached = localStorage.getItem('rates_cache');
        if (cached) {
            const parsed = JSON.parse(cached);
            updateDOM(parsed);
        }
    } catch(e) {}

    // Fetch fresh rates in case they changed
    fetch('/data/rates.json')
        .then(res => res.json())
        .then(data => {
            updateDOM(data);
        })
        .catch(err => console.error("Error fetching live rates for snapshot:", err));
}

// 2. SVG Graph Engine
let chartState = {
    period: '7d',
    rawPoints: [],
    sortedDaily: [],
    monthlyAverages: [],
    monthsShort: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    labels: {
        street: 'Street Rate',
        official: 'Official Rate',
        premium: 'Premium'
    }
};

function initHistoryChart() {
    const cardEl = document.getElementById('chart-card');
    if (!cardEl) return;

    // Load translated labels and month lists from data attributes
    if (cardEl.dataset.streetLabel) chartState.labels.street = cardEl.dataset.streetLabel;
    if (cardEl.dataset.officialLabel) chartState.labels.official = cardEl.dataset.officialLabel;
    if (cardEl.dataset.premiumLabel) chartState.labels.premium = cardEl.dataset.premiumLabel;
    
    try {
        if (cardEl.dataset.monthsShort) {
            chartState.monthsShort = JSON.parse(cardEl.dataset.monthsShort);
        }
    } catch (e) {}

    // Extract raw points
    const rawEl = document.getElementById('history-raw-data');
    if (rawEl) {
        try {
            chartState.rawPoints = JSON.parse(rawEl.textContent);
        } catch (e) {
            console.error("Failed to parse script points:", e);
            return;
        }
    }

    if (!chartState.rawPoints || chartState.rawPoints.length === 0) {
        document.getElementById('chart-canvas-container').innerHTML = `
            <div class="flex h-full items-center justify-center text-xs font-semibold text-slate-400">
                No historical rate data available.
            </div>
        `;
        return;
    }

    // Sort chronologically ascending (oldest to newest for plotting left-to-right)
    chartState.sortedDaily = [...chartState.rawPoints].sort((a, b) => a.date.localeCompare(b.date));

    // Compute monthly averages
    computeMonthlyAverages();

    // Trigger initial draw
    drawChart();

    // Make chart responsive
    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
            drawChart();
        }, 150);
    });

    // Handle system color theme changes
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.attributeName === 'class') {
                drawChart();
            }
        });
    });
    observer.observe(document.documentElement, { attributes: true });
}

function computeMonthlyAverages() {
    const groups = {};
    chartState.sortedDaily.forEach(p => {
        const monthKey = p.date.substring(0, 7); // "YYYY-MM"
        if (!groups[monthKey]) {
            groups[monthKey] = { sumStreet: 0, sumOfficial: 0, count: 0 };
        }
        groups[monthKey].sumStreet += p.street;
        groups[monthKey].sumOfficial += p.official;
        groups[monthKey].count += 1;
    });

    chartState.monthlyAverages = Object.keys(groups).sort().map(monthKey => {
        const g = groups[monthKey];
        const avgStreet = g.sumStreet / g.count;
        const avgOfficial = g.sumOfficial / g.count;
        return {
            date: monthKey, // "YYYY-MM"
            street: avgStreet,
            official: avgOfficial,
            premium: ((avgStreet / avgOfficial) - 1) * 100,
            isMonthlyAvg: true
        };
    });
}

// Global button handler
window.changePeriod = function(period) {
    if (chartState.period === period) return;
    chartState.period = period;

    // Toggle button styles
    ['7d', '4w', 'monthly'].forEach(p => {
        const btn = document.getElementById(`btn-${p}`);
        if (!btn) return;
        if (p === period) {
            btn.className = "px-3 py-1.5 text-xs font-bold rounded-md transition-all shadow-sm bg-white text-slate-900 dark:bg-card-dark dark:text-white";
        } else {
            btn.className = "px-3 py-1.5 text-xs font-bold rounded-md transition-all text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white";
        }
    });

    // Draw
    drawChart();
};

function formatDateLabel(dateStr, isMonthly) {
    if (isMonthly) {
        // "YYYY-MM" -> Short Month Name
        const monthIdx = parseInt(dateStr.split('-')[1], 10) - 1;
        const year = dateStr.split('-')[0].substring(2); // last two digits
        const monthName = chartState.monthsShort[monthIdx] || dateStr;
        return `${monthName} '${year}`;
    } else {
        // "YYYY-MM-DD" -> "DD MMM"
        const parts = dateStr.split('-');
        const day = parseInt(parts[2], 10);
        const monthIdx = parseInt(parts[1], 10) - 1;
        const monthName = chartState.monthsShort[monthIdx] || parts[1];
        return `${day} ${monthName}`;
    }
}

function drawChart() {
    const container = document.getElementById('chart-canvas-container');
    if (!container) return;

    container.innerHTML = '';

    const width = container.clientWidth;
    const height = container.clientHeight;

    // Filter points based on period
    let points = [];
    if (chartState.period === '7d') {
        points = chartState.sortedDaily.slice(-7);
    } else if (chartState.period === '4w') {
        points = chartState.sortedDaily.slice(-28);
    } else if (chartState.period === 'monthly') {
        points = chartState.monthlyAverages;
    }

    if (points.length === 0) {
        container.innerHTML = `
            <div class="flex h-full items-center justify-center text-xs font-semibold text-slate-400">
                No data available for this range.
            </div>
        `;
        return;
    }

    const totalPoints = points.length;

    // Chart margins
    const isMobile = width < 480;
    const margin = {
        top: 15,
        right: 15,
        bottom: 30,
        left: isMobile ? 32 : 40
    };

    const plotWidth = width - margin.left - margin.right;
    const plotHeight = height - margin.top - margin.bottom;

    // Find min / max rates
    const allVals = points.flatMap(p => [p.street, p.official]);
    let minVal = Math.min(...allVals);
    let maxVal = Math.max(...allVals);
    let diff = maxVal - minVal;
    if (diff < 1) diff = 1;

    // Pad Y-axis slightly for aesthetics
    const padding = diff * 0.15;
    const minY = Math.max(0, minVal - padding);
    const maxY = maxVal + padding;

    // Dark/Light Theme values
    const isDark = document.documentElement.classList.contains('dark');
    const gridColor = isDark ? 'rgba(255, 255, 255, 0.06)' : 'rgba(15, 23, 42, 0.05)';
    const axisTextColor = isDark ? 'rgba(255, 255, 255, 0.45)' : 'rgba(71, 85, 105, 0.6)';
    const textFamily = 'Plus Jakarta Sans, sans-serif';

    // 1. Create primary SVG element
    const svgNamespace = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(svgNamespace, "svg");
    svg.setAttribute("width", "100%");
    svg.setAttribute("height", "100%");
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    svg.style.overflow = "visible";

    // 2. Define Gradient defs
    const defs = document.createElementNS(svgNamespace, "defs");
    defs.innerHTML = `
        <linearGradient id="streetGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#17b0cf" stop-opacity="0.18" />
            <stop offset="100%" stop-color="#17b0cf" stop-opacity="0.00" />
        </linearGradient>
    `;
    svg.appendChild(defs);

    // 3. Coordinate mapping helper
    function getX(i) {
        if (totalPoints <= 1) return margin.left + plotWidth / 2;
        return margin.left + (i / (totalPoints - 1)) * plotWidth;
    }

    function getY(val) {
        return margin.top + plotHeight - ((val - minY) / (maxY - minY)) * plotHeight;
    }

    // 4. Draw Horizontal Gridlines (Y ticks)
    const yTicks = 4;
    for (let i = 0; i <= yTicks; i++) {
        const val = minY + (i / yTicks) * (maxY - minY);
        const y = getY(val);

        // Gridline path
        const gridLine = document.createElementNS(svgNamespace, "line");
        gridLine.setAttribute("x1", margin.left);
        gridLine.setAttribute("y1", y);
        gridLine.setAttribute("x2", width - margin.right);
        gridLine.setAttribute("y2", y);
        gridLine.setAttribute("stroke", gridColor);
        gridLine.setAttribute("stroke-width", "1");
        svg.appendChild(gridLine);

        // Y Axis Label
        const yText = document.createElementNS(svgNamespace, "text");
        yText.setAttribute("x", margin.left - 8);
        yText.setAttribute("y", y + 3.5);
        yText.setAttribute("text-anchor", "end");
        yText.setAttribute("fill", axisTextColor);
        yText.setAttribute("font-size", isMobile ? "9px" : "11px");
        yText.setAttribute("font-weight", "600");
        yText.setAttribute("font-family", textFamily);
        yText.textContent = val.toFixed(1);
        svg.appendChild(yText);
    }

    // 5. Compute drawing coordinates for line paths
    const chartCoords = points.map((p, i) => ({
        x: getX(i),
        yStreet: getY(p.street),
        yOfficial: getY(p.official),
        data: p
    }));

    // 6. Draw Street rate filled area under curve
    let streetAreaPathData = `M ${chartCoords[0].x} ${margin.top + plotHeight} `;
    chartCoords.forEach(c => {
        streetAreaPathData += `L ${c.x} ${c.yStreet} `;
    });
    streetAreaPathData += `L ${chartCoords[chartCoords.length - 1].x} ${margin.top + plotHeight} Z`;

    const streetArea = document.createElementNS(svgNamespace, "path");
    streetArea.setAttribute("d", streetAreaPathData);
    streetArea.setAttribute("fill", "url(#streetGrad)");
    svg.appendChild(streetArea);

    // 7. Draw Official rate dashed line
    let officialLinePathData = `M ${chartCoords[0].x} ${chartCoords[0].yOfficial} `;
    for (let i = 1; i < chartCoords.length; i++) {
        officialLinePathData += `L ${chartCoords[i].x} ${chartCoords[i].yOfficial} `;
    }

    const officialLine = document.createElementNS(svgNamespace, "path");
    officialLine.setAttribute("d", officialLinePathData);
    officialLine.setAttribute("fill", "none");
    officialLine.setAttribute("stroke", isDark ? "rgba(255,255,255,0.3)" : "rgba(100,116,139,0.4)");
    officialLine.setAttribute("stroke-width", "2");
    officialLine.setAttribute("stroke-dasharray", "4,4");
    svg.appendChild(officialLine);

    // 8. Draw Street rate main stroke line
    let streetLinePathData = `M ${chartCoords[0].x} ${chartCoords[0].yStreet} `;
    for (let i = 1; i < chartCoords.length; i++) {
        streetLinePathData += `L ${chartCoords[i].x} ${chartCoords[i].yStreet} `;
    }

    const streetLine = document.createElementNS(svgNamespace, "path");
    streetLine.setAttribute("d", streetLinePathData);
    streetLine.setAttribute("fill", "none");
    streetLine.setAttribute("stroke", "#17b0cf");
    streetLine.setAttribute("stroke-width", isMobile ? "2.5" : "3.5");
    streetLine.setAttribute("stroke-linecap", "round");
    streetLine.setAttribute("stroke-linejoin", "round");
    svg.appendChild(streetLine);

    // 9. Draw X-axis label ticks
    let labelsToDraw = [];
    if (chartState.period === '7d' || chartState.period === 'monthly') {
        // Draw every point label
        labelsToDraw = chartCoords;
    } else {
        // 4W: Draw about 4 or 5 labels evenly spaced
        const step = Math.ceil(totalPoints / 4);
        chartCoords.forEach((c, idx) => {
            if (idx === 0 || idx === totalPoints - 1 || idx % step === 0) {
                labelsToDraw.push(c);
            }
        });
    }

    labelsToDraw.forEach(c => {
        const xText = document.createElementNS(svgNamespace, "text");
        xText.setAttribute("x", c.x);
        xText.setAttribute("y", margin.top + plotHeight + (isMobile ? 14 : 18));
        xText.setAttribute("text-anchor", "middle");
        xText.setAttribute("fill", axisTextColor);
        xText.setAttribute("font-size", isMobile ? "8px" : "10px");
        xText.setAttribute("font-weight", "600");
        xText.setAttribute("font-family", textFamily);
        xText.textContent = formatDateLabel(c.data.date, c.data.isMonthlyAvg);
        svg.appendChild(xText);
    });

    // 10. Interactive Tracker Line & Circles (Initially hidden)
    const trackerGroup = document.createElementNS(svgNamespace, "g");
    trackerGroup.style.display = "none";

    // Tracker line
    const trackingLine = document.createElementNS(svgNamespace, "line");
    trackingLine.setAttribute("y1", margin.top);
    trackingLine.setAttribute("y2", margin.top + plotHeight);
    trackingLine.setAttribute("stroke", isDark ? "rgba(255,255,255,0.15)" : "rgba(15,23,42,0.1)");
    trackingLine.setAttribute("stroke-width", "1.5");
    trackerGroup.appendChild(trackingLine);

    // Official Rate Tracker dot
    const officialDot = document.createElementNS(svgNamespace, "circle");
    officialDot.setAttribute("r", isMobile ? "3" : "4.5");
    officialDot.setAttribute("fill", isDark ? "#1e293b" : "#ffffff");
    officialDot.setAttribute("stroke", isDark ? "rgba(255,255,255,0.4)" : "rgba(100,116,139,0.5)");
    officialDot.setAttribute("stroke-width", "2");
    trackerGroup.appendChild(officialDot);

    // Street Rate Tracker dot (vibrant outer ring and dot)
    const streetDotGlow = document.createElementNS(svgNamespace, "circle");
    streetDotGlow.setAttribute("r", isMobile ? "6" : "8");
    streetDotGlow.setAttribute("fill", "#17b0cf");
    streetDotGlow.setAttribute("fill-opacity", "0.25");
    trackerGroup.appendChild(streetDotGlow);

    const streetDot = document.createElementNS(svgNamespace, "circle");
    streetDot.setAttribute("r", isMobile ? "3.5" : "5");
    streetDot.setAttribute("fill", "#ffffff");
    streetDot.setAttribute("stroke", "#17b0cf");
    streetDot.setAttribute("stroke-width", "2.5");
    trackerGroup.appendChild(streetDot);

    svg.appendChild(trackerGroup);
    container.appendChild(svg);

    // 11. Mouse & Touch interactions logic
    const tooltip = document.getElementById('chart-tooltip');

    function hideTooltip() {
        trackerGroup.style.display = "none";
        if (tooltip) {
            tooltip.style.opacity = "0";
            tooltip.style.pointerEvents = "none";
        }
    }

    function showTooltipAt(clampedIdx) {
        const coord = chartCoords[clampedIdx];
        if (!coord) return;

        // Position SVGs tracker elements
        trackingLine.setAttribute("x1", coord.x);
        trackingLine.setAttribute("x2", coord.x);

        officialDot.setAttribute("cx", coord.x);
        officialDot.setAttribute("cy", coord.yOfficial);

        streetDotGlow.setAttribute("cx", coord.x);
        streetDotGlow.setAttribute("cy", coord.yStreet);
        streetDot.setAttribute("cx", coord.x);
        streetDot.setAttribute("cy", coord.yStreet);

        trackerGroup.style.display = "inline";

        // Draw and place dynamic tooltip
        if (tooltip) {
            const dateStr = formatDateLabel(coord.data.date, coord.data.isMonthlyAvg);
            const premiumPct = ((coord.data.street / coord.data.official) - 1) * 100;

            document.getElementById('tooltip-date').textContent = dateStr;
            document.getElementById('tooltip-street-val').textContent = `${coord.data.street.toFixed(2)} BOB`;
            document.getElementById('tooltip-official-val').textContent = `${coord.data.official.toFixed(2)} BOB`;
            document.getElementById('tooltip-premium-val').textContent = `+${premiumPct.toFixed(1)}%`;

            // Tooltip relative placement
            const tooltipWidth = tooltip.offsetWidth || 150;
            const tooltipHeight = tooltip.offsetHeight || 90;

            // X Placement (centered on coordinate, clamped within canvas margins)
            let tx = coord.x;
            if (tx - tooltipWidth / 2 < 10) {
                tx = tooltipWidth / 2 + 10;
            } else if (tx + tooltipWidth / 2 > width - 10) {
                tx = width - tooltipWidth / 2 - 10;
            }

            // Y Placement (placed just above the higher rate point, or fixed offset)
            const higherY = Math.min(coord.yStreet, coord.yOfficial);
            let ty = higherY - tooltipHeight - 12;
            if (ty < 5) {
                // If it pushes out of bounds on top, flip below the point
                ty = Math.max(coord.yStreet, coord.yOfficial) + 12;
            }

            tooltip.style.left = `${tx}px`;
            tooltip.style.top = `${ty}px`;
            tooltip.style.opacity = "1";
        }
    }

    function handleInteraction(clientX) {
        const rect = container.getBoundingClientRect();
        const cursorX = clientX - rect.left;

        // Map cursor relative X coordinate to grid spacing index
        if (cursorX >= margin.left - 10 && cursorX <= width - margin.right + 10) {
            const relativeX = cursorX - margin.left;
            const percent = relativeX / plotWidth;
            let index = Math.round(percent * (totalPoints - 1));
            index = Math.max(0, Math.min(totalPoints - 1, index));

            showTooltipAt(index);
        } else {
            hideTooltip();
        }
    }

    // Bind event listeners
    container.addEventListener('mousemove', (e) => {
        handleInteraction(e.clientX);
    });

    container.addEventListener('mouseleave', () => {
        hideTooltip();
    });

    // Touch events for full mobile drag experience
    container.addEventListener('touchstart', (e) => {
        if (e.touches.length > 0) {
            handleInteraction(e.touches[0].clientX);
        }
    }, { passive: true });

    container.addEventListener('touchmove', (e) => {
        if (e.touches.length > 0) {
            handleInteraction(e.touches[0].clientX);
        }
    }, { passive: true });

    container.addEventListener('touchend', () => {
        hideTooltip();
    });
}
