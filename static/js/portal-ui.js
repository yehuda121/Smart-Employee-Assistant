/**
 * Reusable IT Portal UI components: confirmation modal, form modal, and toast notifications.
 */
(function (global) {
  "use strict";

  var TOAST_DURATION_MS = 4000;
  var INFO_TOAST_DURATION_MS = 5000;
  var toastQueue = [];
  var toastVisible = false;
  var activeModalCleanup = null;

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function getModalRoot() {
    return document.getElementById("portal-modal-root");
  }

  function getToastContainer() {
    return document.getElementById("portal-toast-container");
  }

  function cleanupModalBindings() {
    if (typeof activeModalCleanup === "function") {
      activeModalCleanup();
      activeModalCleanup = null;
    }
  }

  function closeModal(root) {
    if (!root) {
      return;
    }
    cleanupModalBindings();
    root.hidden = true;
    root.classList.remove("is-open");
    document.body.classList.remove("portal-modal-open");
  }

  function openModal(root) {
    cleanupModalBindings();
    root.hidden = false;
    requestAnimationFrame(function () {
      root.classList.add("is-open");
    });
    document.body.classList.add("portal-modal-open");
  }

  function bindModalDismiss(root, onCancel) {
    var overlay = root.querySelector(".portal-modal-overlay");
    var cancelButtons = root.querySelectorAll("[data-modal-cancel]");

    function handleCancel() {
      closeModal(root);
      if (typeof onCancel === "function") {
        onCancel();
      }
    }

    function escHandler(event) {
      if (event.key === "Escape" && !root.hidden) {
        handleCancel();
      }
    }

    overlay.addEventListener("click", handleCancel);
    cancelButtons.forEach(function (button) {
      button.addEventListener("click", handleCancel);
    });
    document.addEventListener("keydown", escHandler);

    activeModalCleanup = function () {
      overlay.removeEventListener("click", handleCancel);
      cancelButtons.forEach(function (button) {
        button.removeEventListener("click", handleCancel);
      });
      document.removeEventListener("keydown", escHandler);
    };
  }

  function confirm(options) {
    options = options || {};
    var root = getModalRoot();
    if (!root) {
      return Promise.resolve(false);
    }
    var dialog = root.querySelector(".portal-modal-dialog");
    var titleEl = root.querySelector("#portal-modal-title");
    var messageEl = root.querySelector("#portal-modal-message");
    var confirmBtn = root.querySelector("[data-modal-confirm]");
    var formEl = root.querySelector("#portal-modal-form");

    formEl.hidden = true;
    dialog.hidden = false;
    titleEl.textContent = options.title || "Confirm action";
    messageEl.textContent = options.message || "Are you sure you want to continue?";
    confirmBtn.textContent = options.confirmLabel || "Confirm";
    confirmBtn.className = options.danger ? "btn btn-danger" : "btn btn-primary";

    openModal(root);

    return new Promise(function (resolve) {
      var settled = false;

      function finish(result) {
        if (settled) {
          return;
        }
        settled = true;
        confirmBtn.removeEventListener("click", onConfirm);
        closeModal(root);
        resolve(result);
      }

      function onConfirm() {
        finish(true);
      }

      bindModalDismiss(root, function () {
        finish(false);
      });

      confirmBtn.addEventListener("click", onConfirm);
      confirmBtn.focus();
    });
  }

  function confirmUnsyncedLeave(options) {
    options = options || {};
    var isLogout = options.context === "logout";
    var leaveLabel = isLogout ? "Logout Without Syncing" : "Leave Without Syncing";
    var syncLabel = isLogout ? "Sync and Logout" : "Sync and Leave";

    return showChoiceModal({
      title: "Unsynced Knowledge Base Changes",
      message:
        "You have unsynced Knowledge Base changes.\n\n" +
        "These changes are saved to the Knowledge Base source file, but they are not available to employees until synchronization is completed.",
      buttons: [
        { label: "Cancel", value: "cancel", className: "btn btn-secondary" },
        { label: leaveLabel, value: "leave", className: "btn btn-secondary" },
        { label: syncLabel, value: "sync-leave", className: "btn btn-primary" },
      ],
    });
  }

  function showChoiceModal(options) {
    options = options || {};
    var root = getModalRoot();
    if (!root) {
      return Promise.resolve("cancel");
    }
    var dialog = root.querySelector(".portal-modal-dialog");
    var formEl = root.querySelector("#portal-modal-form");
    var titleEl = root.querySelector("#portal-modal-title");
    var messageEl = root.querySelector("#portal-modal-message");
    var actionsEl = dialog.querySelector(".portal-modal-actions");
    var defaultActionsHtml = actionsEl.innerHTML;

    formEl.hidden = true;
    dialog.hidden = false;
    titleEl.textContent = options.title || "Confirm action";
    messageEl.textContent = options.message || "";

    actionsEl.innerHTML = "";
    (options.buttons || []).forEach(function (buttonConfig) {
      var button = document.createElement("button");
      button.type = "button";
      button.className = buttonConfig.className || "btn btn-secondary";
      button.textContent = buttonConfig.label;
      button.setAttribute("data-choice-value", buttonConfig.value);
      actionsEl.appendChild(button);
    });
    actionsEl.classList.add("portal-modal-actions--multi");

    openModal(root);

    return new Promise(function (resolve) {
      var settled = false;

      function finish(value) {
        if (settled) {
          return;
        }
        settled = true;
        actionsEl.innerHTML = defaultActionsHtml;
        actionsEl.classList.remove("portal-modal-actions--multi");
        closeModal(root);
        resolve(value);
      }

      bindModalDismiss(root, function () {
        finish("cancel");
      });

      actionsEl.querySelectorAll("[data-choice-value]").forEach(function (button) {
        button.addEventListener("click", function () {
          finish(button.getAttribute("data-choice-value"));
        });
      });

      var firstButton = actionsEl.querySelector("button");
      if (firstButton) {
        firstButton.focus();
      }
    });
  }

  function showFormModal(options) {
    options = options || {};
    var root = getModalRoot();
    if (!root) {
      return Promise.resolve(null);
    }
    var dialog = root.querySelector(".portal-modal-dialog");
    var formEl = root.querySelector("#portal-modal-form");
    var titleEl = root.querySelector("#portal-form-title");
    var fieldsEl = root.querySelector("#portal-form-fields");
    var submitBtn = root.querySelector("[data-form-submit]");
    var errorEl = root.querySelector("#portal-form-error");

    dialog.hidden = true;
    formEl.hidden = false;
    errorEl.hidden = true;
    errorEl.textContent = "";
    titleEl.textContent = options.title || "Knowledge Entry";
    submitBtn.textContent = options.submitLabel || "Save";

    fieldsEl.innerHTML = "";
    (options.fields || []).forEach(function (field) {
      var wrapper = document.createElement("div");
      wrapper.className = "portal-form-field";

      var label = document.createElement("label");
      label.className = "form-label";
      label.setAttribute("for", field.id);
      label.textContent = field.label + (field.required ? " *" : "");

      var input;
      if (field.type === "textarea") {
        input = document.createElement("textarea");
        input.rows = field.rows || 4;
      } else {
        input = document.createElement("input");
        input.type = "text";
      }

      input.id = field.id;
      input.name = field.name;
      input.className = field.type === "textarea" ? "form-input" : "form-input form-input--single";
      input.value = field.value || "";
      input.required = Boolean(field.required);

      wrapper.appendChild(label);
      wrapper.appendChild(input);
      fieldsEl.appendChild(wrapper);
    });

    openModal(root);

    return new Promise(function (resolve) {
      function finish(result) {
        formEl.removeEventListener("submit", onSubmit);
        closeModal(root);
        resolve(result);
      }

      bindModalDismiss(root, function () {
        finish(null);
      });

      function onSubmit(event) {
        event.preventDefault();
        var values = {};
        var valid = true;

        (options.fields || []).forEach(function (field) {
          var input = formEl.querySelector('[name="' + field.name + '"]');
          var value = input ? input.value.trim() : "";
          if (field.required && !value) {
            valid = false;
          }
          values[field.name] = value;
        });

        if (!valid) {
          errorEl.textContent = "Please complete all required fields.";
          errorEl.hidden = false;
          return;
        }

        finish(values);
      }

      formEl.addEventListener("submit", onSubmit);
      var firstInput = fieldsEl.querySelector("input, textarea");
      if (firstInput) {
        firstInput.focus();
      }
    });
  }

  function showFormError(message) {
    var errorEl = document.querySelector("#portal-form-error");
    if (!errorEl) {
      return;
    }
    errorEl.textContent = message;
    errorEl.hidden = false;
  }

  function processToastQueue() {
    if (toastVisible || toastQueue.length === 0) {
      return;
    }

    toastVisible = true;
    var item = toastQueue.shift();
    var container = getToastContainer();
    var toast = document.createElement("div");
    toast.className = "portal-toast portal-toast--" + item.type;
    toast.setAttribute("role", item.type === "error" ? "alert" : "status");
    toast.innerHTML =
      '<span class="portal-toast-icon" aria-hidden="true"></span>' +
      '<span class="portal-toast-message">' + escapeHtml(item.message) + "</span>";

    container.appendChild(toast);
    requestAnimationFrame(function () {
      toast.classList.add("is-visible");
    });

    window.setTimeout(function () {
      toast.classList.remove("is-visible");
      window.setTimeout(function () {
        toast.remove();
        toastVisible = false;
        processToastQueue();
      }, 250);
    }, item.durationMs || TOAST_DURATION_MS);
  }

  function enqueueToast(type, message, durationMs) {
    var container = getToastContainer();
    if (!container) {
      return;
    }

    toastQueue.push({
      type: type,
      message: message,
      durationMs: durationMs || TOAST_DURATION_MS,
    });
    processToastQueue();
  }

  function toastSuccess(message) {
    enqueueToast("success", message);
  }

  function toastError(message) {
    enqueueToast("error", message);
  }

  function toastInfo(message, durationMs) {
    enqueueToast("info", message, durationMs || INFO_TOAST_DURATION_MS);
  }

  function toastWarning(message, durationMs) {
    enqueueToast("info", message, durationMs || INFO_TOAST_DURATION_MS);
  }

  global.PortalUI = {
    confirm: confirm,
    confirmUnsyncedLeave: confirmUnsyncedLeave,
    showChoiceModal: showChoiceModal,
    showFormModal: showFormModal,
    showFormError: showFormError,
    toastSuccess: toastSuccess,
    toastError: toastError,
    toastInfo: toastInfo,
    toastWarning: toastWarning,
    escapeHtml: escapeHtml,
  };
})(window);
