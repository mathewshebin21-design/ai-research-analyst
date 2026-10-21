import fs from "node:fs";

import { expect, test } from "@playwright/test";

const shots = process.env.E2E_SHOTS;
async function shot(page: import("@playwright/test").Page, name: string) {
  if (shots) await page.screenshot({ path: `${shots}/${name}.png`, fullPage: true });
}

test("market-entry question to defensible report", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("link", { name: "Sign in" }).click();
  await page.getByLabel("Email").fill("analyst@example.com");
  await page.getByRole("button", { name: "Sign in" }).click();

  // Consent is required and recorded before the product can be used.
  await expect(page).toHaveURL(/accept-terms/);
  await expect(page.getByRole("button", { name: "Accept and continue" })).toBeDisabled();
  await page.getByRole("checkbox").check();
  await page.getByRole("button", { name: "Accept and continue" }).click();
  await expect(page.getByRole("heading", { name: "What decision are you making?" })).toBeVisible();

  // Upload an internal PDF; it is cited by page later.
  await page.locator("#upload").setInputFiles("e2e/fixtures/memo.pdf");
  await expect(page.getByText("memo.pdf")).toBeVisible();

  await page.getByLabel("Market-entry question").fill("Should we launch sustainable trainers online in the UK in 2027?");
  await page.getByRole("button", { name: "Draft research plan" }).click();

  // Research plan: reviewed and edited before anything is searched.
  await expect(page.getByRole("heading", { name: "Research plan" })).toBeVisible();
  await expect(page.getByLabel("Task 1 title")).toHaveValue("UK online footwear market growth");
  await page.getByLabel("Task 3 search 1").fill("northfold trainer price uk");
  await shot(page, "01-plan");
  await page.getByRole("button", { name: "Approve plan and start research" }).click();

  // Run completes; the executive dashboard appears.
  await expect(page.getByRole("button", { name: "Executive dashboard" })).toBeVisible({ timeout: 60_000 });
  await expect(page.getByText("Recommendation", { exact: true })).toBeVisible();
  await expect(page.getByText(/Confidence (Low|Moderate|High)/)).toBeVisible();
  await expect(page.getByText("Held at 50")).toBeVisible(); // unevidenced factor score is not trusted
  await shot(page, "02-dashboard");

  // Change an assumption: the Python engine recalculates; save a new version.
  const before = await page.getByText("Peak funding need").first().locator("..").innerText();
  const slider = page.getByRole("slider", { name: "Acquisition cost per customer" });
  await slider.focus();
  for (let i = 0; i < 25; i++) await page.keyboard.press("ArrowRight");
  await expect(page.getByText("Your input").first()).toBeVisible();
  await expect.poll(async () => page.getByText("Peak funding need").first().locator("..").innerText()).not.toBe(before);
  await page.getByRole("button", { name: "Save as new version" }).click();
  await expect(page.getByText("Saved versions: v1, v2")).toBeVisible();

  // Export the board report as a real PDF.
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export board report" }).click();
  const file = await (await download).path();
  expect(fs.readFileSync(file!).subarray(0, 4).toString()).toBe("%PDF");

  // Evidence inspector: contradicted claim with its exact quote.
  await page.getByRole("button", { name: "Evidence inspector" }).click();
  await page.getByRole("button", { name: /^Contradicted/ }).click();
  await expect(page.getByRole("heading", { name: /premium of at least 20%/ })).toBeVisible();
  await expect(page.locator("article mark").first()).toContainText("median acceptable premium");
  await page.getByRole("button", { name: /^All claims/ }).click();
  await page.getByRole("button", { name: /Online footwear sales in the United Kingdom grew by 6.5% in 2025$/ }).first().click();
  await expect(page.getByText(/page 1/).first()).toBeVisible();
  await shot(page, "03-evidence");

  // Research workspace: real sources and frameworks.
  await page.getByRole("button", { name: "Research workspace" }).click();
  await expect(page.getByRole("heading", { name: "Sources" })).toBeVisible();
  await expect(page.getByRole("link", { name: /Fixture: footwear retail sales bulletin/ })).toBeVisible();
  await shot(page, "04-workspace");

  // Account: data export works.
  await page.getByRole("link", { name: "Account and data" }).click();
  const exportDl = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export my data" }).click();
  const exported = JSON.parse(fs.readFileSync((await (await exportDl).path())!, "utf8"));
  expect(exported.workspaces[0].runs[0].question).toContain("sustainable trainers");

  // Legal pages render from the shared Markdown.
  await page.goto("/legal/privacy");
  await expect(page.getByRole("heading", { name: "Privacy Notice" })).toBeVisible();
  await expect(page.getByText("ico.org.uk/make-a-complaint")).toBeVisible();
});
