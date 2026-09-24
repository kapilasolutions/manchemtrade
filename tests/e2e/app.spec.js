
import { test, expect } from '@playwright/test';

test.describe('ManchemTrade LIVE v3.8.3 E2E', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
  });

  test('SPX chain never shows undefined', async ({ page }) => {
    await page.click('[data-ticker="SPX"]');
    await page.waitForSelector('#chainTableBody');
    const body = await page.locator('#chainTableBody').innerText();
    expect(body).not.toContain('undefined');
    expect(body).not.toContain('$NaN');
    await expect(page.locator('#tradingHeader')).not.toContainText('undefined');
  });

  test('Market status badge shows Closed or Open, not blank', async ({ page }) => {
    await page.click('[data-ticker="SPX"]');
    await expect(page.locator('#marketStatus')).toContainText(/Market:/);
  });

  test('Calls/Puts buttons are next to Option Chain label', async ({ page }) => {
    const header = page.locator('text=OPTION CHAIN');
    await expect(header).toBeVisible();
    await expect(page.locator('#callsBtn')).toBeVisible();
    await expect(page.locator('#putsBtn')).toBeVisible();
  });

  test('Strategy buttons exist instead of dropdown', async ({ page }) => {
    await expect(page.locator('#strategyButtons')).toBeVisible();
    await expect(page.locator('[data-strat="Single Call"]')).toBeVisible();
    await expect(page.locator('[data-strat="Butterfly (3 legs)"]')).toBeVisible();
  });

  test('Put Credit Spread auto-switches to Puts', async ({ page }) => {
    await page.click('[data-strat="Put Credit Spread"]');
    // Puts button should become active blue
    await expect(page.locator('#putsBtn')).toHaveClass(/bg-\[#4c8bff\]/);
  });

  test('Butterfly shows 3 legs', async ({ page }) => {
    await page.click('[data-strat="Butterfly (3 legs)"]');
    await expect(page.locator('#leg3SingleCont')).toBeVisible();
  });
});
