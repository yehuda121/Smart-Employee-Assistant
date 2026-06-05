/**
 * IT Portal application logic: Analytics and Knowledge Base tabs.
 */
(function () {
  "use strict";

  var config = window.IT_PORTAL_CONFIG || {};
  var PAGE_SIZE = 10;
  var ANSWER_PREVIEW_LENGTH = 140;

  var analyticsRecords = [];
  var knowledgeRecords = [];
  var analyticsSort = { field: "count", direction: "desc" };
  var knowledgeSort = { field: "question", direction: "asc" };
  var knowledgeSearch = "";
  var knowledgePage = 1;
  var syncState = {
    isSynced: true,
    lastSyncRequestedDisplay: "Not available",
  };
  var isSyncing = false;
  var allowNavigationWithoutSyncWarning = false;

  function hasPendingSync() {
    return syncState.isSynced === false;
  }

  function shouldWarnBeforeUnload() {
    return hasPendingSync() && !allowNavigationWithoutSyncWarning;
  }

  function normalizeSyncStatus(status) {
    if (!status || typeof status.isSynced !== "boolean") {
      return null;
    }
    return {
      isSynced: status.isSynced,
      lastSyncRequestedAt: status.lastSyncRequestedAt || null,
      lastSyncRequestedDisplay: status.lastSyncRequestedDisplay || "Not available",
    };
  }

  function extractSyncStatus(data) {
    if (!data) {
      return null;
    }
    return normalizeSyncStatus(data.syncStatus || data);
  }

  function $(selector, root) {
    return (root || document).querySelector(selector);
  }

  function $all(selector, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(selector));
  }

  function fetchJson(url, options) {
    return fetch(url, options).then(function (response) {
      return response.json().then(function (data) {
        return { ok: response.ok, status: response.status, data: data };
      });
    });
  }

  function applySyncStatus(status) {
    var normalized = normalizeSyncStatus(status);
    if (!normalized) {
      return;
    }
    syncState.isSynced = normalized.isSynced;
    syncState.lastSyncRequestedDisplay = normalized.lastSyncRequestedDisplay;
    updateSyncUI();
  }

  function updateSyncUI() {
    var banner = $("#kb-unsynced-banner");
    if (banner) {
      banner.hidden = !hasPendingSync();
    }
    var lastSyncValue = $("#kb-last-sync-value");
    if (lastSyncValue) {
      lastSyncValue.textContent = syncState.lastSyncRequestedDisplay;
    }
  }

  function setSyncButtonSyncing(syncing) {
    var syncBtn = $("#knowledge-sync-btn");
    if (!syncBtn) {
      return;
    }

    var spinner = syncBtn.querySelector(".knowledge-sync-btn-spinner");
    var label = syncBtn.querySelector(".knowledge-sync-btn-text");

    syncBtn.disabled = syncing;
    syncBtn.classList.toggle("is-syncing", syncing);
    syncBtn.setAttribute("aria-busy", syncing ? "true" : "false");
    if (label) {
      label.textContent = syncing ? "Starting Sync..." : "Sync Knowledge Base";
    }
    if (spinner) {
      spinner.hidden = !syncing;
    }
  }

  function refreshSyncStatus() {
    if (!config.knowledgeSyncStatusUrl) {
      return Promise.resolve(false);
    }

    return fetchJson(config.knowledgeSyncStatusUrl, {
      headers: { Accept: "application/json" },
    })
      .then(function (result) {
        if (result.ok && result.data.success) {
          var status = extractSyncStatus(result.data);
          if (status) {
            applySyncStatus(status);
            return true;
          }
        }
        return false;
      })
      .catch(function () {
        return false;
      });
  }

  function triggerSync() {
    if (isSyncing) {
      return Promise.resolve(false);
    }

    isSyncing = true;
    setSyncButtonSyncing(true);

    return fetchJson(config.knowledgeSyncUrl, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
    })
      .then(function (result) {
        if (result.ok && result.data.success) {
          var status = extractSyncStatus(result.data);
          if (status) {
            applySyncStatus(status);
          }
          PortalUI.toastSuccess(
            result.data.message || "Knowledge Base synchronization started successfully."
          );
          return true;
        }
        PortalUI.toastError(result.data.error || "Synchronization failed.");
        return false;
      })
      .catch(function () {
        PortalUI.toastError("Synchronization failed.");
        return false;
      })
      .finally(function () {
        isSyncing = false;
        setSyncButtonSyncing(false);
      });
  }

  function handleProtectedNavigation(proceedFn, context, options) {
    options = options || {};

    if (!hasPendingSync()) {
      proceedFn();
      return;
    }

    PortalUI.confirmUnsyncedLeave({ context: context }).then(function (choice) {
      if (choice === "cancel") {
        return;
      }
      if (choice === "leave") {
        if (options.skipBeforeUnloadWarning) {
          allowNavigationWithoutSyncWarning = true;
        }
        proceedFn();
        return;
      }
      if (choice === "sync-leave") {
        triggerSync().then(function (success) {
          if (success) {
            if (options.skipBeforeUnloadWarning) {
              allowNavigationWithoutSyncWarning = true;
            }
            proceedFn();
          }
        });
      }
    });
  }

  function initLeaveProtection() {
    window.addEventListener("beforeunload", function (event) {
      if (shouldWarnBeforeUnload()) {
        event.preventDefault();
        event.returnValue = "";
      }
    });

    var homeLink = $("#portal-home-link");
    if (homeLink) {
      homeLink.addEventListener("click", function (event) {
        if (!hasPendingSync()) {
          return;
        }
        event.preventDefault();
        handleProtectedNavigation(function () {
          window.location.href = config.homeUrl;
        }, "leave", { skipBeforeUnloadWarning: true });
      });
    }

    var logoutForm = $("#portal-logout-form");
    if (logoutForm) {
      logoutForm.addEventListener("submit", function (event) {
        if (!hasPendingSync()) {
          return;
        }
        event.preventDefault();
        handleProtectedNavigation(function () {
          logoutForm.submit();
        }, "logout", { skipBeforeUnloadWarning: true });
      });
    }
  }

  function showInitialSyncToast() {
    if (hasPendingSync()) {
      PortalUI.toastInfo(
        "There are unsynchronized Knowledge Base changes. Employees will not see updates until synchronization is performed."
      );
    }
  }

  function activateTab(tabName) {
    switchTab(tabName);
    if (tabName === "knowledge") {
      loadKnowledgeEntries();
    }
  }

  function switchTab(tabName) {
    $all(".portal-tab").forEach(function (button) {
      var active = button.getAttribute("data-tab") === tabName;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-selected", active ? "true" : "false");
    });

    $all(".portal-tab-panel").forEach(function (panel) {
      panel.hidden = panel.getAttribute("data-tab-panel") !== tabName;
    });

    var intro = $("#portal-tab-intro");
    if (intro) {
      intro.textContent =
        tabName === "knowledge"
          ? "Manage Knowledge Base source entries in S3. Changes save immediately and remain pending until you synchronize with Bedrock."
          : "Review employee question usage metrics. Removing an analytics record affects DynamoDB only and does not change Knowledge Base content.";
    }
  }

  function compareAnalytics(field, direction, left, right) {
    var multiplier = direction === "desc" ? -1 : 1;

    if (field === "question") {
      return multiplier * (left.question || "").toLowerCase().localeCompare((right.question || "").toLowerCase());
    }

    if (field === "count" || field === "fallbackCount") {
      return multiplier * ((Number(left[field]) || 0) - (Number(right[field]) || 0));
    }

    var dateA = left[field] || "";
    var dateB = right[field] || "";
    if (!dateA && !dateB) return 0;
    if (!dateA) return 1;
    if (!dateB) return -1;
    return multiplier * (dateA < dateB ? -1 : 1);
  }

  function sortItems(items, field, direction, compareFn) {
    return items.slice().sort(function (left, right) {
      var result = compareFn(field, direction, left, right);
      if (result !== 0) {
        return result;
      }
      return (left.question || "").toLowerCase().localeCompare((right.question || "").toLowerCase());
    });
  }

  function updateSortHeaders(containerSelector, activeSort) {
    $all(containerSelector + " .portal-sort-btn").forEach(function (button) {
      var field = button.getAttribute("data-sort-field");
      var th = button.closest("th");
      var arrow = button.querySelector(".portal-sort-arrow");
      var isActive = field === activeSort.field;

      button.classList.toggle("is-active", isActive);
      if (th) {
        th.setAttribute("aria-sort", isActive ? activeSort.direction + "ending" : "none");
      }
      if (arrow) {
        arrow.textContent = isActive ? (activeSort.direction === "desc" ? "↓" : "↑") : "";
      }
    });
  }

  function handleAnalyticsSort(field) {
    if (analyticsSort.field === field) {
      analyticsSort.direction = analyticsSort.direction === "desc" ? "asc" : "desc";
    } else {
      analyticsSort.field = field;
      analyticsSort.direction = "desc";
    }
    renderAnalyticsTable();
    updateSortHeaders("#analytics-table", analyticsSort);
  }

  function renderAnalyticsTable() {
    var tbody = $("#analytics-tbody");
    var tableWrap = $("#portal-analytics-table-wrap");
    var emptyEl = $("#portal-analytics-empty");
    if (!tbody) {
      return;
    }

    var sorted = sortItems(analyticsRecords, analyticsSort.field, analyticsSort.direction, compareAnalytics);
    tbody.innerHTML = "";

    sorted.forEach(function (row) {
      var tr = document.createElement("tr");

      ["question", "count", "fallbackCount"].forEach(function (key, index) {
        var td = document.createElement("td");
        td.className = index === 0 ? "portal-table-question" : "portal-table-num";
        td.textContent = String(row[key]);
        tr.appendChild(td);
      });

      var lastAsked = document.createElement("td");
      lastAsked.className = "portal-table-date";
      lastAsked.textContent = row.lastAskedAtDisplay || "—";
      tr.appendChild(lastAsked);

      var created = document.createElement("td");
      created.className = "portal-table-date";
      created.textContent = row.createdAtDisplay || "—";
      tr.appendChild(created);

      var actions = document.createElement("td");
      actions.className = "portal-table-actions";
      var deleteBtn = document.createElement("button");
      deleteBtn.type = "button";
      deleteBtn.className = "btn btn-danger btn-sm";
      deleteBtn.textContent = "Delete";
      deleteBtn.addEventListener("click", function () {
        confirmDeleteAnalytics(row);
      });
      actions.appendChild(deleteBtn);
      tr.appendChild(actions);

      tbody.appendChild(tr);
    });

    var hasRows = sorted.length > 0;
    tableWrap.hidden = !hasRows;
    emptyEl.hidden = hasRows;
  }

  function confirmDeleteAnalytics(row) {
    PortalUI.confirm({
      title: "Delete Analytics Record",
      message:
        "Are you sure you want to delete this analytics record?\n\n" +
        row.question +
        "\n\nThis removes the record from DynamoDB only. Knowledge Base content, S3 files, and Bedrock indexes are not affected.",
      confirmLabel: "Delete",
      danger: true,
    }).then(function (confirmed) {
      if (!confirmed) {
        return;
      }

      fetchJson(config.analyticsDeleteUrlTemplate.replace("__ID__", encodeURIComponent(row.questionId)), {
        method: "DELETE",
        headers: { Accept: "application/json" },
      })
        .then(function (result) {
          if (result.ok && result.data.success) {
            analyticsRecords = analyticsRecords.filter(function (item) {
              return item.questionId !== row.questionId;
            });
            renderAnalyticsTable();
            PortalUI.toastSuccess(result.data.message || "Analytics record deleted successfully.");
          } else {
            PortalUI.toastError(result.data.error || "Unable to delete record.");
          }
        })
        .catch(function () {
          PortalUI.toastError("Unable to delete record.");
        });
    });
  }

  function initAnalytics() {
    var dataEl = $("#analytics-data");
    if (!dataEl) {
      return;
    }

    try {
      analyticsRecords = JSON.parse(dataEl.textContent || "[]");
    } catch (err) {
      analyticsRecords = [];
    }

    $all("#analytics-table .portal-sort-btn").forEach(function (button) {
      button.addEventListener("click", function () {
        handleAnalyticsSort(button.getAttribute("data-sort-field"));
      });
    });

    renderAnalyticsTable();
    updateSortHeaders("#analytics-table", analyticsSort);
  }

  function filterKnowledgeRecords() {
    var query = knowledgeSearch.toLowerCase();
    if (!query) {
      return knowledgeRecords.slice();
    }

    return knowledgeRecords.filter(function (row) {
      return (
        (row.question || "").toLowerCase().indexOf(query) !== -1 ||
        (row.answer || "").toLowerCase().indexOf(query) !== -1 ||
        (row.category || "").toLowerCase().indexOf(query) !== -1 ||
        (row.keywords || "").toLowerCase().indexOf(query) !== -1
      );
    });
  }

  function compareKnowledge(field, direction, left, right) {
    var multiplier = direction === "desc" ? -1 : 1;
    var valueA = (left[field] || "").toLowerCase();
    var valueB = (right[field] || "").toLowerCase();
    return multiplier * valueA.localeCompare(valueB);
  }

  function handleKnowledgeSort(field) {
    if (knowledgeSort.field === field) {
      knowledgeSort.direction = knowledgeSort.direction === "desc" ? "asc" : "desc";
    } else {
      knowledgeSort.field = field;
      knowledgeSort.direction = "desc";
    }
    knowledgePage = 1;
    renderKnowledgeTable();
    updateSortHeaders("#knowledge-table", knowledgeSort);
  }

  function renderKnowledgeTable() {
    var tbody = $("#knowledge-tbody");
    var tableWrap = $("#portal-knowledge-table-wrap");
    var emptyEl = $("#portal-knowledge-empty");
    var pagination = $("#knowledge-pagination");
    if (!tbody) {
      return;
    }

    var filtered = sortItems(
      filterKnowledgeRecords(),
      knowledgeSort.field,
      knowledgeSort.direction,
      compareKnowledge
    );

    var totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
    if (knowledgePage > totalPages) {
      knowledgePage = totalPages;
    }

    var start = (knowledgePage - 1) * PAGE_SIZE;
    var pageItems = filtered.slice(start, start + PAGE_SIZE);

    tbody.innerHTML = "";
    pageItems.forEach(function (row) {
      var tr = document.createElement("tr");

      var questionCell = document.createElement("td");
      questionCell.className = "portal-table-question";
      questionCell.textContent = row.question;
      tr.appendChild(questionCell);

      var answerCell = document.createElement("td");
      answerCell.className = "portal-table-answer";
      var preview = document.createElement("div");
      preview.className = "portal-answer-preview";
      var fullText = row.answer || "";
      var truncated = fullText.length > ANSWER_PREVIEW_LENGTH;
      preview.textContent = truncated ? fullText.slice(0, ANSWER_PREVIEW_LENGTH) + "…" : fullText;
      answerCell.appendChild(preview);

      if (truncated) {
        var expandBtn = document.createElement("button");
        expandBtn.type = "button";
        expandBtn.className = "portal-link-btn";
        expandBtn.textContent = "Show full answer";
        expandBtn.addEventListener("click", function () {
          var expanded = answerCell.classList.toggle("is-expanded");
          preview.textContent = expanded ? fullText : fullText.slice(0, ANSWER_PREVIEW_LENGTH) + "…";
          expandBtn.textContent = expanded ? "Show less" : "Show full answer";
        });
        answerCell.appendChild(expandBtn);
      }
      tr.appendChild(answerCell);

      var categoryCell = document.createElement("td");
      categoryCell.className = "portal-table-category";
      categoryCell.textContent = row.category;
      tr.appendChild(categoryCell);

      var keywordsCell = document.createElement("td");
      keywordsCell.className = "portal-table-keywords";
      keywordsCell.textContent = row.keywords || "—";
      tr.appendChild(keywordsCell);

      var actionsCell = document.createElement("td");
      actionsCell.className = "portal-table-actions portal-table-actions--split";
      var editBtn = document.createElement("button");
      editBtn.type = "button";
      editBtn.className = "btn btn-secondary btn-sm";
      editBtn.textContent = "Edit";
      editBtn.addEventListener("click", function () {
        openKnowledgeForm("edit", row);
      });
      var deleteBtn = document.createElement("button");
      deleteBtn.type = "button";
      deleteBtn.className = "btn btn-danger btn-sm";
      deleteBtn.textContent = "Delete";
      deleteBtn.addEventListener("click", function () {
        confirmDeleteKnowledge(row);
      });
      actionsCell.appendChild(editBtn);
      actionsCell.appendChild(deleteBtn);
      tr.appendChild(actionsCell);

      tbody.appendChild(tr);
    });

    var hasRows = filtered.length > 0;
    tableWrap.hidden = !hasRows;
    emptyEl.hidden = hasRows;
    if (!hasRows) {
      emptyEl.textContent =
        knowledgeRecords.length > 0 && knowledgeSearch
          ? "No entries match your search."
          : "No Knowledge Base entries are available.";
    }
    pagination.hidden = !hasRows;

    if (!pagination.hidden) {
      $("#knowledge-page-info").textContent = "Page " + knowledgePage + " of " + totalPages;
      $("#knowledge-prev-btn").disabled = knowledgePage <= 1;
      $("#knowledge-next-btn").disabled = knowledgePage >= totalPages;
    }
  }

  function loadKnowledgeEntries() {
    var loadingEl = $("#portal-knowledge-loading");
    loadingEl.hidden = false;

    return fetchJson(config.knowledgeListUrl, { headers: { Accept: "application/json" } })
      .then(function (result) {
        loadingEl.hidden = true;
        if (result.ok && result.data.success) {
          knowledgeRecords = result.data.entries || [];
          var status = extractSyncStatus(result.data);
          if (status) {
            applySyncStatus(status);
          }
          knowledgePage = 1;
          renderKnowledgeTable();
          updateSortHeaders("#knowledge-table", knowledgeSort);
        } else {
          PortalUI.toastError(result.data.error || "Unable to load Knowledge Base entries.");
        }
      })
      .catch(function () {
        loadingEl.hidden = true;
        PortalUI.toastError("Unable to load Knowledge Base entries.");
      });
  }

  function knowledgeFormFields(row) {
    row = row || {};
    return [
      { id: "kb-question", name: "question", label: "Question", value: row.question || "", required: true, type: "textarea", rows: 3 },
      { id: "kb-answer", name: "answer", label: "Answer", value: row.answer || "", required: true, type: "textarea", rows: 5 },
      { id: "kb-category", name: "category", label: "Category", value: row.category || "", required: true },
      { id: "kb-keywords", name: "keywords", label: "Keywords", value: row.keywords || "", required: false },
    ];
  }

  function openKnowledgeForm(mode, row) {
    PortalUI.showFormModal({
      title: mode === "edit" ? "Edit Knowledge Entry" : "Add Knowledge Entry",
      submitLabel: mode === "edit" ? "Save changes" : "Add entry",
      fields: knowledgeFormFields(row),
    }).then(function (values) {
      if (!values) {
        return;
      }

      var url = mode === "edit" ? config.knowledgeUpdateUrlTemplate.replace("__ID__", encodeURIComponent(row.id)) : config.knowledgeListUrl;
      var method = mode === "edit" ? "PUT" : "POST";

      fetchJson(url, {
        method: method,
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify(values),
      })
        .then(function (result) {
          if (result.ok && result.data.success) {
            PortalUI.toastSuccess(result.data.message || "Knowledge entry saved successfully.");
            var savedStatus = extractSyncStatus(result.data);
            if (savedStatus) {
              applySyncStatus(savedStatus);
            }
            loadKnowledgeEntries();
          } else {
            PortalUI.toastError(result.data.error || "Unable to save knowledge entry.");
          }
        })
        .catch(function () {
          PortalUI.toastError("Unable to save knowledge entry.");
        });
    });
  }

  function confirmDeleteKnowledge(row) {
    PortalUI.confirm({
      title: "Delete Knowledge Entry",
      message:
        "Are you sure you want to delete this knowledge entry?\n\n" +
        row.question +
        "\n\nThis removes the record from the Knowledge Base source file and uploads the updated CSV to S3. Synchronization with Bedrock will be required before employees see the change.",
      confirmLabel: "Delete",
      danger: true,
    }).then(function (confirmed) {
      if (!confirmed) {
        return;
      }

      fetchJson(config.knowledgeDeleteUrlTemplate.replace("__ID__", encodeURIComponent(row.id)), {
        method: "DELETE",
        headers: { Accept: "application/json" },
      })
        .then(function (result) {
          if (result.ok && result.data.success) {
            PortalUI.toastSuccess(result.data.message || "Knowledge entry deleted successfully.");
            var deletedStatus = extractSyncStatus(result.data);
            if (deletedStatus) {
              applySyncStatus(deletedStatus);
            }
            loadKnowledgeEntries();
          } else {
            PortalUI.toastError(result.data.error || "Unable to delete knowledge entry.");
          }
        })
        .catch(function () {
          PortalUI.toastError("Unable to delete knowledge entry.");
        });
    });
  }

  function initKnowledge() {
    $("#knowledge-search").addEventListener("input", function (event) {
      knowledgeSearch = event.target.value.trim();
      knowledgePage = 1;
      renderKnowledgeTable();
    });

    $("#knowledge-add-btn").addEventListener("click", function () {
      openKnowledgeForm("add");
    });

    $("#knowledge-sync-btn").addEventListener("click", function () {
      triggerSync();
    });

    $("#knowledge-prev-btn").addEventListener("click", function () {
      if (knowledgePage > 1) {
        knowledgePage -= 1;
        renderKnowledgeTable();
      }
    });

    $("#knowledge-next-btn").addEventListener("click", function () {
      knowledgePage += 1;
      renderKnowledgeTable();
    });

    $all("#knowledge-table .portal-sort-btn").forEach(function (button) {
      button.addEventListener("click", function () {
        handleKnowledgeSort(button.getAttribute("data-sort-field"));
      });
    });

    $all(".portal-tab").forEach(function (button) {
      button.addEventListener("click", function () {
        var tab = button.getAttribute("data-tab");
        var activeTab = $(".portal-tab.is-active");
        var currentTab = activeTab ? activeTab.getAttribute("data-tab") : "analytics";

        if (currentTab === "knowledge" && tab !== "knowledge" && hasPendingSync()) {
          handleProtectedNavigation(function () {
            activateTab(tab);
          }, "leave");
          return;
        }

        activateTab(tab);
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    if (!window.PortalUI) {
      return;
    }

    setSyncButtonSyncing(false);
    initAnalytics();
    initKnowledge();
    initLeaveProtection();

    refreshSyncStatus()
      .then(function (refreshed) {
        if (!refreshed && config.initialSyncStatus) {
          applySyncStatus(config.initialSyncStatus);
        }
      })
      .finally(function () {
        showInitialSyncToast();
        switchTab("analytics");
      });
  });
})();
