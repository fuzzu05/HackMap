import { test, expect } from '@playwright/test';

test.describe('Authentication and Core Flow', () => {
  test('homepage loads and shows global hackathons', async ({ page }) => {
    await page.goto('/');
    
    // Check SEO Title
    await expect(page).toHaveTitle(/HackMap/);

    // Verify main components render
    // Depending on what Yusra built, we assume there's a heading or a login button
    const heading = page.locator('h1, h2, h3').first();
    await expect(heading).toBeVisible();
  });
});
