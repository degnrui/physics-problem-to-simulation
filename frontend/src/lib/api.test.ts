import { exportDownloadUrl, resolveApiBase } from "./api";

describe("api base resolution", () => {
  it("defaults to same-origin api routes", () => {
    expect(resolveApiBase()).toBe("/api");
  });

  it("builds download urls from the resolved base", () => {
    expect(exportDownloadUrl("run-123")).toBe("/api/problem-to-simulation/runs/run-123/export-html");
  });
});
