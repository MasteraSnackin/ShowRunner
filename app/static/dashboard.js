const state = {
  events: [],
  pendingPayoutId: null,
  loading: false,
};

const elements = {
  eventGrid: document.getElementById("eventGrid"),
  skeletonGrid: document.getElementById("skeletonGrid"),
  emptyState: document.getElementById("emptyState"),
  errorState: document.getElementById("errorState"),
  errorMessage: document.getElementById("errorMessage"),
  statusBanner: document.getElementById("statusBanner"),
  totalCount: document.getElementById("totalCount"),
  openCount: document.getElementById("openCount"),
  readyCount: document.getElementById("readyCount"),
  settledCount: document.getElementById("settledCount"),
  composerPanel: document.getElementById("composerPanel"),
  composerForm: document.getElementById("composerForm"),
  confirmDialog: document.getElementById("confirmDialog"),
  toastStack: document.getElementById("toastStack"),
};

function showToast(message, kind = "success") {
  const toast = document.createElement("div");
  toast.className = `toast ${kind === "error" ? "error" : ""}`.trim();
  toast.textContent = message;
  elements.toastStack.appendChild(toast);
  window.setTimeout(() => toast.remove(), 2800);
}

function setLoading(loading, label = "Loading dashboard") {
  state.loading = loading;
  elements.statusBanner.textContent = label;
  elements.skeletonGrid.classList.toggle("hidden", !loading);
  if (loading) {
    elements.errorState.classList.add("hidden");
    elements.emptyState.classList.add("hidden");
    elements.eventGrid.classList.add("hidden");
  }
}

function setCounts(counts) {
  elements.totalCount.textContent = counts.total ?? 0;
  elements.openCount.textContent = counts.open ?? 0;
  elements.readyCount.textContent = counts.ready_for_payout ?? 0;
  elements.settledCount.textContent = counts.settled ?? 0;
}

function updateBanner(message) {
  elements.statusBanner.textContent = message;
}

function setOptimisticStatus(eventId, status) {
  state.events = state.events.map((event) =>
    event.id === eventId
      ? {
          ...event,
          status,
          actions: {
            ...event.actions,
            can_settle: false,
            can_payout: status === "ready_for_payout",
          },
        }
      : event
  );
  renderEvents();
}

function renderEvents() {
  elements.skeletonGrid.classList.add("hidden");
  elements.errorState.classList.add("hidden");

  if (!state.events.length) {
    elements.emptyState.classList.remove("hidden");
    elements.eventGrid.classList.add("hidden");
    updateBanner("No events staged yet");
    return;
  }

  elements.emptyState.classList.add("hidden");
  elements.eventGrid.classList.remove("hidden");
  elements.eventGrid.innerHTML = "";

  for (const event of state.events) {
    const card = document.createElement("article");
    card.className = "event-card";
    const actionButtons = [];

    actionButtons.push(`
      <button class="action-button add-sale-button" data-event-id="${event.id}" ${
        !event.actions.can_record_sale ? "disabled" : ""
      }>
        Record sale
      </button>
    `);

    actionButtons.push(`
      <button class="action-button settle-button" data-event-id="${event.id}" ${
        !event.actions.can_settle ? "disabled" : ""
      }>
        Settle
      </button>
    `);

    actionButtons.push(`
      <button class="action-button payout-button" data-event-id="${event.id}" ${
        !event.actions.can_payout ? "disabled" : ""
      }>
        Approve payout
      </button>
    `);

    card.innerHTML = `
      <div class="event-banner" style="background-image: linear-gradient(180deg, rgba(16, 23, 22, 0.08), rgba(16, 23, 22, 0.5)), linear-gradient(135deg, rgba(31, 92, 87, 0.78), rgba(221, 108, 66, 0.88)), url('${event.banner_url}')">
        <div class="event-title">${event.title}</div>
      </div>
      <div class="status-chip status-${event.status}">${event.status.replaceAll("_", " ")}</div>
      <div>${event.description}</div>
      <div class="metric-row">
        <div class="metric-pill"><span>Price</span><strong>$${Number(event.price).toFixed(2)}</strong></div>
        <div class="metric-pill"><span>Supply</span><strong>${event.supply}</strong></div>
        <div class="metric-pill"><span>Chain ID</span><strong>${event.onchain_event_id ?? "n/a"}</strong></div>
      </div>
      <div class="sale-popover hidden" id="sale-popover-${event.id}">
        <label>
          Ticket quantity
          <input type="number" min="1" max="25" value="1" id="sale-input-${event.id}" />
        </label>
        <div class="sale-popover-actions">
          <button class="secondary-button cancel-sale" data-event-id="${event.id}" type="button">Cancel</button>
          <button class="primary-button confirm-sale" data-event-id="${event.id}" type="button">Record</button>
        </div>
      </div>
      <div class="card-actions">${actionButtons.join("")}</div>
    `;

    elements.eventGrid.appendChild(card);
  }
}

async function fetchDashboard() {
  setLoading(true);
  try {
    const response = await fetch("/api/events");
    if (!response.ok) {
      throw new Error(`Dashboard request failed (${response.status})`);
    }
    const payload = await response.json();
    state.events = payload.events ?? [];
    setCounts(payload.counts ?? {});
    renderEvents();
    updateBanner(state.events.length ? "Live event board synced" : "Ready for your first event");
  } catch (error) {
    elements.skeletonGrid.classList.add("hidden");
    elements.eventGrid.classList.add("hidden");
    elements.emptyState.classList.add("hidden");
    elements.errorState.classList.remove("hidden");
    elements.errorMessage.textContent = error.message;
    updateBanner("Connection issue");
    showToast(error.message, "error");
  }
}

async function mutate(url, options, successMessage) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || `Request failed (${response.status})`);
  }
  const result = await response.json();
  showToast(successMessage);
  await fetchDashboard();
  return result;
}

function openComposer() {
  elements.composerPanel.classList.remove("hidden");
}

function closeComposer() {
  elements.composerPanel.classList.add("hidden");
}

function openSalePopover(eventId) {
  document
    .querySelectorAll(".sale-popover")
    .forEach((popover) => popover.classList.add("hidden"));
  document.getElementById(`sale-popover-${eventId}`)?.classList.remove("hidden");
}

function closeSalePopover(eventId) {
  document.getElementById(`sale-popover-${eventId}`)?.classList.add("hidden");
}

async function createSampleEvent() {
  openComposer();
  elements.composerForm.requestSubmit();
}

document.getElementById("openComposer").addEventListener("click", openComposer);
document.getElementById("heroCreate").addEventListener("click", openComposer);
document.getElementById("emptyCreate").addEventListener("click", createSampleEvent);
document.getElementById("seedEvent").addEventListener("click", createSampleEvent);
document.getElementById("closeComposer").addEventListener("click", closeComposer);
document.getElementById("heroRefresh").addEventListener("click", fetchDashboard);
document.getElementById("retryLoad").addEventListener("click", fetchDashboard);

elements.composerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const submitButton = elements.composerForm.querySelector("button[type='submit']");
  submitButton.disabled = true;
  updateBanner("Creating event");
  const formData = new FormData(elements.composerForm);
  const payload = Object.fromEntries(formData.entries());
  try {
    await mutate(
      "/api/demo/events",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      },
      "Event created"
    );
    closeComposer();
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    submitButton.disabled = false;
  }
});

elements.eventGrid.addEventListener("click", async (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement)) {
    return;
  }

  const eventId = Number(target.dataset.eventId);
  if (!eventId) {
    return;
  }

  if (target.classList.contains("add-sale-button")) {
    openSalePopover(eventId);
    return;
  }

  if (target.classList.contains("cancel-sale")) {
    closeSalePopover(eventId);
    return;
  }

  if (target.classList.contains("confirm-sale")) {
    const input = document.getElementById(`sale-input-${eventId}`);
    const quantity = Number(input?.value || 1);
    target.disabled = true;
    updateBanner("Recording sale");
    try {
      await mutate(
        `/api/demo/events/${eventId}/sales`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ quantity }),
        },
        "Sale recorded"
      );
      closeSalePopover(eventId);
    } catch (error) {
      showToast(error.message, "error");
    } finally {
      target.disabled = false;
    }
    return;
  }

  if (target.classList.contains("settle-button")) {
    setOptimisticStatus(eventId, "ready_for_payout");
    target.disabled = true;
    updateBanner("Settling revenue");
    try {
      await mutate(
        `/api/demo/events/${eventId}/settle`,
        { method: "POST" },
        "Settlement prepared"
      );
    } catch (error) {
      showToast(error.message, "error");
      await fetchDashboard();
    }
    return;
  }

  if (target.classList.contains("payout-button")) {
    state.pendingPayoutId = eventId;
    elements.confirmDialog.showModal();
  }
});

elements.confirmDialog.addEventListener("close", async () => {
  if (elements.confirmDialog.returnValue !== "confirm" || !state.pendingPayoutId) {
    state.pendingPayoutId = null;
    return;
  }

  const payoutId = state.pendingPayoutId;
  state.pendingPayoutId = null;
  setOptimisticStatus(payoutId, "settled");
  updateBanner("Approving payout");
  try {
    await mutate(
      `/api/demo/events/${payoutId}/payout`,
      { method: "POST" },
      "Payout approved"
    );
  } catch (error) {
    showToast(error.message, "error");
    await fetchDashboard();
  }
});

fetchDashboard();
