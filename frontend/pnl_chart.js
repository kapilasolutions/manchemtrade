
// P&L Chart Component - ManchemTrade v3.8.4 Feature #1
// Vanilla JS - No dependencies, draws on <canvas id="pnlChart">
class PnLChart {
  constructor(canvasId) {
    this.canvas = document.getElementById(canvasId);
    if (!this.canvas) return;
    this.ctx = this.canvas.getContext('2d');
    this.resize();
    window.addEventListener('resize', () => this.resize());
  }

  resize() {
    if (!this.canvas) return;
    const rect = this.canvas.parentElement.getBoundingClientRect();
    this.canvas.width = rect.width * window.devicePixelRatio;
    this.canvas.height = 300 * window.devicePixelRatio;
    this.canvas.style.width = rect.width + 'px';
    this.canvas.style.height = '300px';
    this.ctx.setTransform(window.devicePixelRatio, 0, 0, window.devicePixelRatio, 0, 0);
    if (this.lastData) this.draw(this.lastData);
  }

  calculatePnL(shortStrike, longStrike, netCredit, isCall) {
    const width = Math.abs(longStrike - shortStrike);
    const maxGain = netCredit;
    const maxLoss = width - netCredit;
    const breakeven = isCall ? shortStrike + netCredit : shortStrike - netCredit;
    const minPrice = Math.min(shortStrike, longStrike) - width;
    const maxPrice = Math.max(shortStrike, longStrike) + width;
    const points = [];
    for (let i = 0; i <= 50; i++) {
      const price = minPrice + (maxPrice - minPrice) * i / 50;
      let pnl;
      if (isCall) {
        if (price <= shortStrike) pnl = maxGain;
        else if (price >= longStrike) pnl = -maxLoss;
        else pnl = maxGain - (price - shortStrike);
      } else {
        if (price >= shortStrike) pnl = maxGain;
        else if (price <= longStrike) pnl = -maxLoss;
        else pnl = maxGain - (shortStrike - price);
      }
      points.push({ price, pnl });
    }
    return { shortStrike, longStrike, width, maxGain, maxLoss, breakeven, points, isCall, netCredit };
  }

  draw(data) {
    this.lastData = data;
    const ctx = this.ctx;
    const W = this.canvas.width / window.devicePixelRatio;
    const H = 300;
    const padding = { top: 20, right: 20, bottom: 40, left: 50 };
    const chartW = W - padding.left - padding.right;
    const chartH = H - padding.top - padding.bottom;

    ctx.clearRect(0, 0, W, H);

    // Find bounds
    const prices = data.points.map(p => p.price);
    const pnls = data.points.map(p => p.pnl);
    const minPrice = Math.min(...prices);
    const maxPrice = Math.max(...prices);
    const minPnL = Math.min(...pnls) * 1.1;
    const maxPnL = Math.max(...pnls) * 1.1;

    const xScale = (price) => padding.left + ((price - minPrice) / (maxPrice - minPrice)) * chartW;
    const yScale = (pnl) => padding.top + chartH - ((pnl - minPnL) / (maxPnL - minPnL)) * chartH;

    // Grid
    ctx.strokeStyle = '#2a2a3a';
    ctx.lineWidth = 1;
    // Zero line
    const zeroY = yScale(0);
    ctx.beginPath();
    ctx.moveTo(padding.left, zeroY);
    ctx.lineTo(W - padding.right, zeroY);
    ctx.strokeStyle = '#555';
    ctx.setLineDash([4, 4]);
    ctx.stroke();
    ctx.setLineDash([]);

    // P&L Line
    ctx.beginPath();
    ctx.strokeStyle = '#00d4aa';
    ctx.lineWidth = 2.5;
    data.points.forEach((p, i) => {
      const x = xScale(p.price);
      const y = yScale(p.pnl);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });
    ctx.stroke();

    // Fill gain/loss
    ctx.lineTo(xScale(maxPrice), zeroY);
    ctx.lineTo(xScale(minPrice), zeroY);
    ctx.closePath();
    const gradient = ctx.createLinearGradient(0, yScale(maxPnL), 0, yScale(minPnL));
    gradient.addColorStop(0, 'rgba(0, 212, 170, 0.3)');
    gradient.addColorStop(0.5, 'rgba(0, 212, 170, 0.05)');
    gradient.addColorStop(1, 'rgba(255, 82, 82, 0.3)');
    ctx.fillStyle = gradient;
    ctx.fill();

    // Markers
    ctx.fillStyle = '#fff';
    ctx.font = '11px monospace';
    // Breakeven
    ctx.fillStyle = '#ffaa00';
    ctx.beginPath();
    ctx.arc(xScale(data.breakeven), zeroY, 4, 0, Math.PI*2);
    ctx.fill();
    ctx.fillText(`BE ${data.breakeven.toFixed(1)}`, xScale(data.breakeven)+6, zeroY-8);

    // Short strike
    ctx.fillStyle = '#ff5252';
    ctx.fillRect(xScale(data.shortStrike)-1, padding.top, 2, chartH);
    ctx.fillText(`Short ${data.shortStrike}`, xScale(data.shortStrike)+4, padding.top+12);

    // Labels
    ctx.fillStyle = '#aaa';
    ctx.fillText(`Max Gain $${data.maxGain.toFixed(2)}`, padding.left, padding.top+12);
    ctx.fillText(`Max Loss $${data.maxLoss.toFixed(2)}`, W - padding.right - 110, padding.top+12);
    ctx.fillText(`R/R ${(data.maxGain/data.maxLoss).toFixed(2)}`, W/2 -20, padding.top+12);

    // X labels
    ctx.fillText(minPrice.toFixed(0), padding.left, H - 8);
    ctx.fillText(maxPrice.toFixed(0), W - padding.right - 30, H - 8);
  }
}

// Auto-init if canvas exists
window.PnLChart = PnLChart;
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('pnlChart')) {
    window.manchemPnLChart = new PnLChart('pnlChart');
  }
});

// Feature #2: Iron Condor Width Auto-Calc
window.calculateIronCondorWidth = function(shortCall, longCall, shortPut, longPut) {
  const callWidth = Math.abs(longCall - shortCall);
  const putWidth = Math.abs(shortPut - longPut);
  const maxWidth = Math.max(callWidth, putWidth);
  const isBalanced = callWidth === putWidth;
  return {
    callWidth, putWidth, maxWidth, isBalanced,
    risk: maxWidth, // max loss wing
    suggestion: isBalanced ? `Balanced ${maxWidth} wide wings ✅` : `Unbalanced! Call ${callWidth} vs Put ${putWidth} — Max risk $${maxWidth}`,
    maxLoss: maxWidth // minus credit, actual max loss calculated with credit
  };
};

// Auto-update UI when Iron Condor selected
document.addEventListener('DOMContentLoaded', () => {
  const strategySelect = document.getElementById('strategy') || document.querySelector('select');
  if (!strategySelect) return;
  
  const checkAndShowWidth = () => {
    const strategy = (strategySelect.value || '').toLowerCase();
    if (strategy.includes('iron') && strategy.includes('condor')) {
      // Try to get strikes from inputs
      const inputs = document.querySelectorAll('input[type="number"]');
      if (inputs.length >= 4) {
        const vals = Array.from(inputs).map(i => parseFloat(i.value)).filter(v => !isNaN(v));
        if (vals.length >= 4) {
          const result = window.calculateIronCondorWidth(vals[0], vals[1], vals[2], vals[3]);
          let badge = document.getElementById('widthBadge');
          if (!badge) {
            badge = document.createElement('div');
            badge.id = 'widthBadge';
            badge.style.cssText = 'margin-top:10px; padding:8px 12px; background:#1a1a2e; border:1px solid #333; border-radius:8px; font-family:monospace; color:#00d4aa;';
            strategySelect.parentElement.appendChild(badge);
          }
          badge.innerHTML = `📐 Call Width: $${result.callWidth} | Put Width: $${result.putWidth} | Max Wing: $${result.maxWidth} ${result.isBalanced ? '✅ Balanced' : '⚠️ Unbalanced'}`;
        }
      }
    }
  };
  
  strategySelect.addEventListener('change', checkAndShowWidth);
  document.addEventListener('input', checkAndShowWidth);
});
