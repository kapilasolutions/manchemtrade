
"""
P&L Calculator for Vertical Spreads - ManchemTrade v3.8.4
Feature #1: P&L Chart for Call Credit Spread / Put Credit Spread
"""
from typing import Dict, List

def calculate_credit_spread_pnl(short_strike: float, long_strike: float, net_credit: float, is_call: bool = True) -> Dict:
    """
    Calculate P&L metrics for a credit spread.
    For Call Credit Spread: short lower? Actually Call Credit = Bear Call: short lower strike? No, Bear Call: short lower, long higher? Wait.
    Bear Call Credit: Sell lower call, Buy higher call. Max gain = credit, Max loss = width - credit.
    Bull Put Credit: Sell higher put, Buy lower put.
    """
    width = abs(long_strike - short_strike)
    if width <= 0:
        raise ValueError("Strikes must be different")
    if net_credit <= 0:
        raise ValueError("Credit spread must have positive net credit")
    if net_credit >= width:
        raise ValueError("Credit cannot exceed width - arbitrage")

    max_gain = net_credit
    max_loss = width - net_credit
    
    # Breakeven
    if is_call:
        # Bear Call: breakeven = short strike + credit (short is lower strike for bear call? Actually bear call short is lower)
        # Let's define short_strike is sold leg
        breakeven = short_strike + net_credit if short_strike < long_strike else short_strike - net_credit
        # Correct logic: For Bear Call (short low call, long high call): BE = short + credit
        # For Bull Put (short high put, long low put): BE = short - credit
        if short_strike < long_strike:  # Bear Call
            breakeven = short_strike + net_credit
        else:  # Should not happen but fallback
            breakeven = short_strike + net_credit
    else:
        # Bull Put: short high put, long low put: BE = short - credit
        breakeven = short_strike - net_credit

    # Generate P&L points for chart
    # X axis: underlying price from (short - width) to (long + width)
    min_price = min(short_strike, long_strike) - width
    max_price = max(short_strike, long_strike) + width
    points = []
    steps = 50
    for i in range(steps+1):
        price = min_price + (max_price - min_price) * i / steps
        if is_call:
            # Bear Call P&L at expiration
            if price <= short_strike:
                pnl = max_gain
            elif price >= long_strike:
                pnl = -max_loss
            else:
                # Linear between
                pnl = max_gain - (price - short_strike)
        else:
            # Bull Put
            if price >= short_strike:
                pnl = max_gain
            elif price <= long_strike:
                pnl = -max_loss
            else:
                pnl = max_gain - (short_strike - price)
        points.append({"price": round(price, 2), "pnl": round(pnl, 2)})

    return {
        "short_strike": short_strike,
        "long_strike": long_strike,
        "width": width,
        "net_credit": net_credit,
        "max_gain": round(max_gain, 2),
        "max_loss": round(max_loss, 2),
        "breakeven": round(breakeven, 2),
        "risk_reward": round(max_gain / max_loss, 2) if max_loss else 0,
        "points": points,
        "is_call": is_call
    }

def calculate_iron_condor_width(short_call: float, long_call: float, short_put: float, long_put: float) -> Dict:
    """
    Feature #2 prep: Iron Condor width auto-calc
    Returns max wing width
    """
    call_width = abs(long_call - short_call)
    put_width = abs(short_put - long_put)
    max_width = max(call_width, put_width)
    return {
        "call_width": call_width,
        "put_width": put_width,
        "max_width": max_width,
        "call_strikes": (short_call, long_call),
        "put_strikes": (long_put, short_put)
    }
