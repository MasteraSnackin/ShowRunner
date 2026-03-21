const pptxgen = require("/tmp/showrunner-pptx-deps/node_modules/pptxgenjs");

const pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "Codex";
pptx.company = "Encode ShowRunner";
pptx.subject = "Hackathon pitch deck";
pptx.title = "Encode ShowRunner";
pptx.lang = "en-GB";
pptx.theme = {
  headFontFace: "Aptos Display",
  bodyFontFace: "Aptos",
  lang: "en-GB",
};

const colors = {
  ink: "1F2937",
  slate: "334155",
  muted: "64748B",
  paper: "F8F5EF",
  card: "FFFDF8",
  sand: "E9DFC9",
  amber: "D97706",
  rust: "C2410C",
  olive: "3F5A48",
  teal: "0F766E",
  red: "B91C1C",
  white: "FFFFFF",
};

function addBackground(slide, accent = colors.sand) {
  slide.background = { color: colors.paper };
  slide.addShape(pptx.ShapeType.rect, {
    x: 0,
    y: 0,
    w: 13.333,
    h: 7.5,
    fill: { color: colors.paper },
    line: { color: colors.paper },
  });
  slide.addShape(pptx.ShapeType.rect, {
    x: 0.4,
    y: 0.35,
    w: 12.55,
    h: 6.8,
    fill: { color: colors.card },
    line: { color: accent, width: 1.25 },
    radius: 0.08,
    shadow: {
      type: "outer",
      color: "C9BFA7",
      blur: 1,
      angle: 45,
      distance: 2,
      opacity: 0.15,
    },
  });
}

function addHeader(slide, section, title, accent = colors.ink) {
  slide.addText(section, {
    x: 0.8,
    y: 0.65,
    w: 2.5,
    h: 0.22,
    fontFace: "Arial",
    fontSize: 11,
    bold: true,
    color: colors.rust,
    charSpace: 1.2,
    allCaps: true,
  });
  slide.addText(title, {
    x: 0.8,
    y: 0.9,
    w: 8.4,
    h: 0.62,
    fontFace: "Georgia",
    fontSize: 25,
    bold: true,
    color: accent,
  });
}

function addFooter(slide, text = "Encode ShowRunner") {
  slide.addText(text, {
    x: 0.8,
    y: 6.9,
    w: 3.0,
    h: 0.2,
    fontFace: "Arial",
    fontSize: 8.5,
    color: colors.muted,
  });
}

function addPill(slide, text, x, y, w, fill, color = colors.white) {
  slide.addText(text, {
    x,
    y,
    w,
    h: 0.34,
    fontFace: "Arial",
    fontSize: 10,
    bold: true,
    align: "center",
    valign: "mid",
    color,
    fill: { color: fill },
    line: { color: fill, width: 1 },
    margin: 0.04,
    radius: 0.08,
  });
}

function addBulletList(slide, items, opts = {}) {
  const x = opts.x ?? 0.9;
  const y = opts.y ?? 1.9;
  const w = opts.w ?? 5.6;
  const h = opts.h ?? 3.8;
  const color = opts.color ?? colors.ink;
  const fontSize = opts.fontSize ?? 18;
  const bulletIndent = opts.bulletIndent ?? 16;
  const hanging = opts.hanging ?? 4;
  const runs = [];
  items.forEach((item) => {
    runs.push({
      text: item,
      options: {
        bullet: { indent: bulletIndent },
        hanging,
        paraSpaceAfterPt: 14,
      },
    });
  });
  slide.addText(runs, {
    x,
    y,
    w,
    h,
    fontFace: "Arial",
    fontSize,
    color,
    breakLine: false,
    valign: "top",
    margin: 0,
  });
}

function addMetricCard(slide, x, y, w, h, title, value, fill, body) {
  slide.addShape(pptx.ShapeType.roundRect, {
    x,
    y,
    w,
    h,
    rectRadius: 0.08,
    fill: { color: fill },
    line: { color: fill, width: 1 },
  });
  slide.addText(title, {
    x: x + 0.18,
    y: y + 0.18,
    w: w - 0.36,
    h: 0.18,
    fontFace: "Arial",
    fontSize: 10,
    bold: true,
    color: colors.muted,
    allCaps: true,
  });
  slide.addText(value, {
    x: x + 0.18,
    y: y + 0.48,
    w: w - 0.36,
    h: 0.45,
    fontFace: "Georgia",
    fontSize: 24,
    bold: true,
    color: colors.ink,
  });
  slide.addText(body, {
    x: x + 0.18,
    y: y + 1.0,
    w: w - 0.36,
    h: h - 1.18,
    fontFace: "Arial",
    fontSize: 11,
    color: colors.slate,
    valign: "top",
    margin: 0,
  });
}

async function main() {
// Slide 1
{
  const slide = pptx.addSlide();
  addBackground(slide, colors.rust);
  slide.addShape(pptx.ShapeType.rect, {
    x: 0.8,
    y: 1.15,
    w: 0.85,
    h: 4.9,
    fill: { color: colors.rust },
    line: { color: colors.rust, width: 1 },
  });
  slide.addText("Encode\nShowRunner", {
    x: 1.05,
    y: 1.2,
    w: 4.9,
    h: 1.75,
    fontFace: "Georgia",
    fontSize: 27,
    bold: true,
    color: colors.ink,
    breakLine: false,
  });
  slide.addText("The AI orchestration layer for event operations", {
    x: 1.08,
    y: 3.0,
    w: 4.9,
    h: 0.45,
    fontFace: "Arial",
    fontSize: 18,
    color: colors.slate,
    bold: true,
  });
  slide.addText(
    "We connect where communities coordinate, where ticketing settles, and where trust needs guardrails.",
    {
      x: 1.08,
      y: 3.58,
      w: 4.8,
      h: 1.1,
      fontFace: "Arial",
      fontSize: 15,
      color: colors.muted,
      valign: "top",
      margin: 0,
    }
  );
  addPill(slide, "Luffa", 1.08, 5.05, 1.05, colors.olive);
  addPill(slide, "Endless", 2.28, 5.05, 1.2, colors.teal);
  addPill(slide, "Civic", 3.64, 5.05, 1.0, colors.amber);
  slide.addText("Hackathon pitch deck", {
    x: 1.08,
    y: 5.62,
    w: 3.5,
    h: 0.22,
    fontFace: "Arial",
    fontSize: 9.5,
    color: colors.muted,
    italic: true,
  });

  addMetricCard(
    slide,
    6.55,
    1.2,
    2.0,
    2.0,
    "Problem",
    "Fragmented ops",
    "F6E9D6",
    "Communication, ticketing, payout, and policy usually live in separate tools."
  );
  addMetricCard(
    slide,
    8.75,
    1.2,
    1.9,
    2.0,
    "Approach",
    "One workflow",
    "E5F1ED",
    "Dashboard and webhook flows run through the same orchestration layer."
  );
  addMetricCard(
    slide,
    10.85,
    1.2,
    1.6,
    2.0,
    "Outcome",
    "Trusted AI",
    "FCE7E5",
    "Automation helps, but guardrails stay in control."
  );

  slide.addShape(pptx.ShapeType.roundRect, {
    x: 6.55,
    y: 3.55,
    w: 5.95,
    h: 2.5,
    rectRadius: 0.06,
    fill: { color: "F7F2E8" },
    line: { color: "D7C7AB", width: 1 },
  });
  slide.addText("Pitch thesis", {
    x: 6.88,
    y: 3.82,
    w: 1.6,
    h: 0.22,
    fontFace: "Arial",
    fontSize: 10,
    bold: true,
    color: colors.rust,
    allCaps: true,
  });
  slide.addText(
    "Events fail in the gaps between platforms.\nShowRunner closes those gaps by orchestrating communication, transaction flow, and trust inside one product.",
    {
      x: 6.88,
      y: 4.2,
      w: 5.05,
      h: 1.4,
      fontFace: "Georgia",
      fontSize: 18,
      color: colors.ink,
      valign: "mid",
      margin: 0,
    }
  );
  addFooter(slide);
}

// Slide 2
{
  const slide = pptx.addSlide();
  addBackground(slide, colors.sand);
  addHeader(slide, "The problem", "Events break when operations are spread across disconnected systems");
  slide.addText(
    "Organisers are forced to jump between chat, admin panels, ticketing tools, and payment approvals. Each handoff adds friction and risk.",
    {
      x: 0.9,
      y: 1.45,
      w: 7.0,
      h: 0.7,
      fontFace: "Arial",
      fontSize: 16,
      color: colors.slate,
      margin: 0,
    }
  );

  addMetricCard(slide, 0.95, 2.35, 3.7, 2.85, "Gap 1", "Coordination lives in chat", "EEF4EF", "Teams already work in conversation-first tools, but event actions still happen elsewhere.");
  addMetricCard(slide, 4.8, 2.35, 3.7, 2.85, "Gap 2", "Ticketing lives in a separate flow", "E8F1F4", "The financial backbone of the event often has no tight connection to the ops workflow.");
  addMetricCard(slide, 8.65, 2.35, 3.7, 2.85, "Gap 3", "Trust is handled manually", "F9ECE7", "Approvals and policy checks become ad hoc, especially when money is involved.");

  slide.addText("Result: teams waste time stitching systems together instead of running the event.", {
    x: 0.95,
    y: 5.75,
    w: 11.4,
    h: 0.35,
    fontFace: "Georgia",
    fontSize: 19,
    bold: true,
    color: colors.ink,
    align: "center",
  });
  addFooter(slide);
}

// Slide 3
{
  const slide = pptx.addSlide();
  addBackground(slide, colors.olive);
  addHeader(slide, "Why these platforms", "We picked one platform for each critical part of the event lifecycle");

  addMetricCard(slide, 0.95, 1.9, 3.8, 3.95, "Luffa", "Where coordination begins", "EDF5EE", "Communities already communicate here. ShowRunner uses Luffa webhooks, commands, and button clicks so the workflow starts where people already are.");
  addMetricCard(slide, 4.77, 1.9, 3.8, 3.95, "Endless", "Where transaction flow happens", "E8F3F2", "Events are not complete until ticketing, settlement, and payout are handled properly. Endless gives ShowRunner a transactional backbone.");
  addMetricCard(slide, 8.59, 1.9, 3.8, 3.95, "Civic", "Where trust is enforced", "FCF0E9", "AI should assist operational decisions, not bypass policy. Civic gives us a guardrail layer before meaningful actions are executed.");

  slide.addText("ShowRunner is the orchestration layer that connects all three.", {
    x: 0.95,
    y: 6.2,
    w: 11.45,
    h: 0.35,
    fontFace: "Georgia",
    fontSize: 20,
    bold: true,
    color: colors.rust,
    align: "center",
  });
  addFooter(slide);
}

// Slide 4
{
  const slide = pptx.addSlide();
  addBackground(slide, colors.teal);
  addHeader(slide, "How it works", "One workflow layer powers both the dashboard and the platform-native experience");
  slide.addText("Current implementation from the repo:", {
    x: 0.95,
    y: 1.52,
    w: 3.2,
    h: 0.2,
    fontFace: "Arial",
    fontSize: 11,
    bold: true,
    color: colors.rust,
    allCaps: true,
  });

  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.95,
    y: 1.9,
    w: 11.45,
    h: 3.8,
    rectRadius: 0.06,
    fill: { color: "F9F6EF" },
    line: { color: "D8CAB4", width: 1 },
  });

  const flowBoxes = [
    { x: 1.25, title: "1. Trigger", body: "Dashboard action or Luffa webhook starts the flow", fill: "F6E9D6" },
    { x: 3.55, title: "2. Orchestrate", body: "FastAPI routes into shared workflows and lifecycle checks", fill: "EAF1EE" },
    { x: 5.85, title: "3. Enrich", body: "LLM generates event copy and banner content when needed", fill: "E7F2F1" },
    { x: 8.15, title: "4. Execute", body: "Endless handles ticketing, settlement summary, and payout simulation", fill: "F8ECE6" },
    { x: 10.45, title: "5. Persist", body: "SQLite stores event state and powers inspection endpoints", fill: "F2EEDF" },
  ];

  flowBoxes.forEach((box) => {
    slide.addShape(pptx.ShapeType.roundRect, {
      x: box.x,
      y: 2.45,
      w: 1.65,
      h: 2.25,
      rectRadius: 0.04,
      fill: { color: box.fill },
      line: { color: box.fill, width: 1 },
    });
    slide.addText(box.title, {
      x: box.x + 0.12,
      y: 2.62,
      w: 1.41,
      h: 0.42,
      fontFace: "Georgia",
      fontSize: 16,
      bold: true,
      color: colors.ink,
      align: "center",
    });
    slide.addText(box.body, {
      x: box.x + 0.1,
      y: 3.18,
      w: 1.45,
      h: 1.1,
      fontFace: "Arial",
      fontSize: 10.5,
      color: colors.slate,
      align: "center",
      valign: "mid",
      margin: 0,
    });
  });

  slide.addText("Architecture: modular monolith today, clean extension points for production integrations tomorrow.", {
    x: 1.1,
    y: 6.02,
    w: 11.0,
    h: 0.28,
    fontFace: "Arial",
    fontSize: 14,
    color: colors.slate,
    align: "center",
  });
  addFooter(slide);
}

// Slide 5
{
  const slide = pptx.addSlide();
  addBackground(slide, colors.amber);
  addHeader(slide, "What we built", "This is already a working prototype, not just a concept");

  addBulletList(slide, [
    "FastAPI backend with browser dashboard and webhook entrypoint",
    "Event creation, sales simulation, settlement, and payout flows",
    "Structured API errors and explicit lifecycle transition guards",
    "SQLite persistence through SQLAlchemy with indexed lookup paths",
    "HTTP-level regression coverage and end-to-end workflow tests",
  ], { x: 0.95, y: 1.95, w: 6.25, h: 3.7, fontSize: 18 });

  addMetricCard(slide, 7.6, 1.9, 2.1, 1.7, "Quality", "29 tests passing", "EDF5EE", "Workflow and route coverage are green in the current repo.");
  addMetricCard(slide, 9.9, 1.9, 2.1, 1.7, "UX", "Dashboard live", "E8F3F2", "Operators can run the lifecycle manually in the browser.");
  addMetricCard(slide, 7.6, 3.9, 2.1, 1.7, "API", "Structured errors", "FCF0E9", "Client-facing failures are consistent and actionable.");
  addMetricCard(slide, 9.9, 3.9, 2.1, 1.7, "State", "Persisted events", "F4EFE1", "Demo data survives requests and can be reset instantly.");

  slide.addText("We are proving that AI-assisted event ops can be practical when orchestration and guardrails come first.", {
    x: 0.95,
    y: 6.15,
    w: 11.1,
    h: 0.35,
    fontFace: "Georgia",
    fontSize: 18,
    bold: true,
    color: colors.rust,
  });
  addFooter(slide);
}

// Slide 6
{
  const slide = pptx.addSlide();
  addBackground(slide, colors.rust);
  slide.addText("Encode ShowRunner", {
    x: 0.95,
    y: 1.05,
    w: 4.2,
    h: 0.5,
    fontFace: "Georgia",
    fontSize: 28,
    bold: true,
    color: colors.ink,
  });
  slide.addText("Closing", {
    x: 0.96,
    y: 1.65,
    w: 1.5,
    h: 0.18,
    fontFace: "Arial",
    fontSize: 10,
    bold: true,
    color: colors.rust,
    allCaps: true,
  });
  slide.addText("ShowRunner turns fragmented event operations into one trusted, AI-assisted workflow.", {
    x: 0.95,
    y: 2.0,
    w: 7.0,
    h: 1.05,
    fontFace: "Georgia",
    fontSize: 24,
    bold: true,
    color: colors.ink,
    margin: 0,
  });
  slide.addText("Communication in Luffa. Transaction flow in Endless. Guardrails in Civic. One orchestration layer on top.", {
    x: 0.95,
    y: 3.25,
    w: 6.4,
    h: 1.0,
    fontFace: "Arial",
    fontSize: 17,
    color: colors.slate,
    margin: 0,
  });
  addPill(slide, "Luffa", 0.95, 4.65, 1.05, colors.olive);
  addPill(slide, "Endless", 2.18, 4.65, 1.15, colors.teal);
  addPill(slide, "Civic", 3.52, 4.65, 1.0, colors.amber);
  addPill(slide, "ShowRunner", 4.7, 4.65, 1.5, colors.rust);

  slide.addShape(pptx.ShapeType.roundRect, {
    x: 7.8,
    y: 1.15,
    w: 4.3,
    h: 4.9,
    rectRadius: 0.08,
    fill: { color: "F8F2E6" },
    line: { color: "DECCAF", width: 1 },
  });
  slide.addText("Judge takeaway", {
    x: 8.1,
    y: 1.45,
    w: 1.9,
    h: 0.2,
    fontFace: "Arial",
    fontSize: 10,
    bold: true,
    color: colors.rust,
    allCaps: true,
  });
  addBulletList(slide, [
    "We chose platforms with complementary roles",
    "We built a working orchestration layer around them",
    "We used AI for leverage, not for uncontrolled decisions",
    "The architecture is ready to swap stubs for production services",
  ], { x: 8.05, y: 1.9, w: 3.55, h: 2.6, fontSize: 15, bulletIndent: 14, hanging: 3 });
  slide.addText("Thank you", {
    x: 8.1,
    y: 5.25,
    w: 2.0,
    h: 0.35,
    fontFace: "Georgia",
    fontSize: 22,
    bold: true,
    color: colors.ink,
  });
  slide.addText("Questions and demo", {
    x: 8.1,
    y: 5.62,
    w: 2.6,
    h: 0.22,
    fontFace: "Arial",
    fontSize: 12,
    color: colors.muted,
  });
  addFooter(slide);
}

await pptx.writeFile({ fileName: "pitch/Encode_ShowRunner_Pitch_Deck.pptx" });
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
