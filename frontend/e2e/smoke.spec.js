import { expect, test } from "@playwright/test";

const password = "supersecret123";

test("smoke: register, expense, report, export", async ({ page }) => {
  const email = `e2e-${Date.now()}@example.com`;

  await page.goto("/register");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: "Register" }).click();

  await expect(page).toHaveURL(/\/login/);
  await expect(page.getByRole("heading", { name: "Sign in", level: 1 })).toBeVisible();

  const loginForm = page.locator("form").filter({
    has: page.getByRole("button", { name: "Sign in" }),
  });
  await loginForm.getByLabel("Email").fill(email);
  await loginForm.getByLabel("Password").fill(password);
  await loginForm.getByRole("button", { name: "Sign in" }).click();

  await expect(page).toHaveURL(/\/expenses/, { timeout: 15_000 });

  await page.goto("/categories");
  await page.getByLabel("New category").fill("Food");
  await page.getByRole("button", { name: "Add" }).click();
  await expect(page.getByText("Food")).toBeVisible();

  await page.goto("/expenses");
  await page.locator("header.view-head").getByRole("button", { name: "Add expense" }).click();
  const expenseForm = page.locator("form").filter({
    has: page.getByRole("spinbutton", { name: "Amount" }),
  });
  await expenseForm.getByRole("spinbutton", { name: "Amount" }).fill("42.50");
  await expenseForm.getByLabel("Category").selectOption({ label: "Food" });
  await expenseForm.getByLabel("Description").fill("E2E groceries");
  await expenseForm.getByLabel("Date").fill("2026-06-15");
  await expenseForm.getByRole("button", { name: "Create expense" }).click();

  await expect(page.getByText("E2E groceries")).toBeVisible();

  await page.goto("/reports");
  await expect(page.getByText("Monthly report")).toBeVisible();

  await page.goto("/export");
  await page.getByRole("button", { name: "Start export" }).click();
  await expect(page.getByText("done")).toBeVisible({ timeout: 90_000 });

  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Download" }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toMatch(/\.csv$/i);
});
