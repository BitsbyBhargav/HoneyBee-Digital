import { test, expect } from "@playwright/test";
import { execFileSync } from "node:child_process";
import path from "node:path";

const formatted = (value) => new Intl.NumberFormat("en-IN").format(value);

test("live MySQL analytics, directory search, filtering and refresh", async ({
  page,
  request,
}) => {
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  const response = await request.get("http://127.0.0.1:8000/api/dashboard");
  const dashboard = await response.json();
  expect(dashboard.summary.total).toBeGreaterThanOrEqual(500);
  await page.setViewportSize({ width: 1440, height: 1100 });
  await page.goto("/");
  const total = page
    .locator(".stat")
    .filter({ hasText: "Total businesses" })
    .locator(":scope > strong");
  await expect(total).toHaveText(formatted(dashboard.summary.total));
  await expect(
    page.getByRole("region", { name: "City-wise business counts" }),
  ).toBeVisible();
  await expect(
    page.getByRole("region", { name: "Category-wise business counts" }),
  ).toBeVisible();
  await expect(
    page.getByRole("region", { name: "Source-wise business counts" }),
  ).toBeVisible();
  await expect(page.locator("tbody .business-cell")).toHaveCount(8);
  await page
    .getByRole("textbox", { name: "Search businesses" })
    .fill("__no_business_matches_this_query__");
  await expect(
    page.getByText("No businesses match these filters.", { exact: false }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Clear filters" }).click();
  await expect(page.locator("tbody .business-cell")).toHaveCount(8);
  await page
    .getByRole("combobox", { name: "Filter by city" })
    .selectOption(dashboard.cities.items[0].name);
  await expect(page.locator(".directory-heading .badge")).toHaveText(
    `${formatted(dashboard.cities.items[0].count)} records`,
  );
  await page.getByRole("button", { name: "Next page" }).click();
  await expect(page.locator(".table-footer")).toContainText("Page 2");
  await page.getByRole("button", { name: "Clear filters" }).click();
  await page.getByRole("button", { name: "Refresh data" }).click();
  await expect(
    page.getByRole("button", { name: "Refresh data" }),
  ).toBeEnabled();
  await expect(page.locator("tbody .business-cell")).toHaveCount(8);
  await page.screenshot({
    path: "../docs/dashboard-desktop.png",
    fullPage: true,
  });
  expect(errors).toEqual([]);
});

test("mobile layout fits viewport and keeps directory usable", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "Listings overview." }),
  ).toBeVisible();
  await expect(page.locator("tbody .business-cell")).toHaveCount(8);
  expect(
    await page.evaluate(() => document.documentElement.scrollWidth),
  ).toBeLessThanOrEqual(390);
  await page
    .getByRole("link", { name: "Business directory", exact: true })
    .click();
  await expect(
    page.getByRole("textbox", { name: "Search businesses" }),
  ).toBeVisible();
  await page.evaluate(() => {
    document.activeElement.blur();
    window.scrollTo({ top: 0, behavior: "instant" });
  });
  await page.screenshot({
    path: "../docs/dashboard-mobile.png",
    fullPage: true,
  });
});

test("loading state, connection failure and recovery", async ({ page }) => {
  let release;
  const gate = new Promise((resolve) => {
    release = resolve;
  });
  await page.route("**/api/dashboard", async (route) => {
    await gate;
    await route.fulfill({
      status: 503,
      json: { detail: "Database unavailable" },
    });
  });
  await page.goto("/");
  await expect(
    page.getByRole("status", { name: "Loading dashboard" }),
  ).toBeVisible();
  release();
  await expect(page.getByRole("alert")).toContainText(
    "We couldn’t refresh your data.",
  );
  await page.unroute("**/api/dashboard");
  await page.getByRole("button", { name: "Try again" }).click();
  await expect(page.locator(".stat")).toHaveCount(4);
  await expect(page.getByRole("alert")).toHaveCount(0);
});

test("empty dataset provides a useful next step", async ({ page }) => {
  const empty = (dimension) => ({ dimension, total: 0, items: [] });
  await page.route("**/api/dashboard", (route) =>
    route.fulfill({
      json: {
        summary: {
          total: 0,
          cities: 0,
          categories: 0,
          sources: 0,
          with_phone: 0,
          latest_import: null,
        },
        cities: empty("city"),
        categories: empty("category"),
        sources: empty("source"),
      },
    }),
  );
  await page.route("**/api/listings?*", (route) =>
    route.fulfill({ json: { items: [], total: 0, page: 1, page_size: 8 } }),
  );
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: "Your directory is ready for data." }),
  ).toBeVisible();
  await expect(
    page.getByText("No businesses match these filters.", { exact: false }),
  ).toBeVisible();
});

test("refresh reflects a real MySQL change and restores the original row", async ({
  page,
}) => {
  const root = path.resolve("..");
  const python = path.join(root, ".venv", "Scripts", "python.exe");
  const helper = path.join(root, "scripts", "refresh_probe.py");
  await page.goto("/");
  await expect(page.locator(".stat")).toHaveCount(4);
  const before = await page.request.get("http://127.0.0.1:8000/api/dashboard");
  const original = await before.json();
  const total = page
    .locator(".stat")
    .filter({ hasText: "Total businesses" })
    .locator(":scope > strong");
  try {
    execFileSync(python, [helper, "remove"], { cwd: root, stdio: "pipe" });
    await page.getByRole("button", { name: "Refresh data" }).click();
    await expect(total).toHaveText(formatted(original.summary.total - 1));
  } finally {
    execFileSync(python, [helper, "restore"], { cwd: root, stdio: "pipe" });
  }
  await page.getByRole("button", { name: "Refresh data" }).click();
  await expect(total).toHaveText(formatted(original.summary.total));
});
