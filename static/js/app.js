(function () {
  function closestSubmitter(event) {
    return event.submitter || document.activeElement;
  }

  document.addEventListener("submit", function (event) {
    const form = event.target;
    const submitter = closestSubmitter(event);
    const confirmMessage = submitter && submitter.getAttribute("data-confirm");

    if (confirmMessage && !window.confirm(confirmMessage)) {
      event.preventDefault();
      return;
    }

    if (form.matches("[data-prevent-double-submit]")) {
      form.querySelectorAll('button[type="submit"]').forEach(function (button) {
        button.disabled = true;
        button.classList.add("is-loading");
      });
    }
  });

  document.addEventListener("htmx:beforeRequest", function (event) {
    const element = event.detail.elt;
    if (element) {
      element.classList.add("is-loading");
    }
  });

  document.addEventListener("htmx:afterRequest", function (event) {
    const element = event.detail.elt;
    if (element) {
      element.classList.remove("is-loading");
    }
  });

  function money(value) {
    return new Intl.NumberFormat("es-MX", {
      style: "currency",
      currency: "MXN",
    }).format(Number(value || 0));
  }

  function initSaleEditor(form) {
    const priceScript = document.getElementById(form.dataset.productPricesId);
    const prices = priceScript ? JSON.parse(priceScript.textContent) : {};
    const rows = form.querySelector("[data-sale-rows]");
    const emptyTemplate = form.querySelector("[data-empty-sale-line]");
    const totalInput = form.querySelector('input[name="lines-TOTAL_FORMS"]');
    const paymentRows = form.querySelector("[data-payment-rows]");
    const emptyPaymentTemplate = form.querySelector("[data-empty-payment-line]");
    const paymentTotalInput = form.querySelector('input[name="payments-TOTAL_FORMS"]');

    if (!rows || !emptyTemplate || !totalInput || !paymentRows || !emptyPaymentTemplate || !paymentTotalInput) {
      return;
    }

    function saleRows() {
      return Array.from(rows.querySelectorAll(".sale-line-row"));
    }

    function rowTotal(row) {
      const productId = row.querySelector('[name$="-product"]')?.value || "";
      const quantity = Number(row.querySelector('[name$="-quantity"]')?.value || 0);
      return Number(prices[productId] || 0) * quantity;
    }

    function paymentLineRows() {
      return Array.from(paymentRows.querySelectorAll(".payment-line-row"));
    }

    function paymentAmount(row) {
      return Number(row.querySelector('[name$="-amount"]')?.value || 0);
    }

    function paymentMethod(row) {
      return row.querySelector('[name$="-payment_method"]')?.value || "CASH";
    }

    function paymentCashReceived(row) {
      const amount = paymentAmount(row);
      const cashValue = row.querySelector('[name$="-cash_received"]')?.value;
      return cashValue !== "" && cashValue !== undefined ? Number(cashValue || 0) : amount;
    }

    function updatePaymentFields(row) {
      const isCash = paymentMethod(row) === "CASH";
      const amount = paymentAmount(row);
      const cashReceived = paymentCashReceived(row);
      const change = isCash ? Math.max(cashReceived - amount, 0) : 0;
      row.querySelectorAll("[data-payment-cash-field]").forEach(function (field) {
        field.classList.toggle("is-hidden", !isCash);
        if (!isCash) {
          field.querySelectorAll("input").forEach(function (input) {
            input.value = "";
          });
        }
      });
      const target = row.querySelector("[data-payment-change]");
      if (target) {
        target.textContent = money(change);
      }
      return { amount, change };
    }

    function updateAlterationFields(row) {
      const toggle = row.querySelector("[data-alteration-toggle]");
      const enabled = Boolean(toggle && toggle.checked);
      row.querySelectorAll("[data-alteration-field]").forEach(function (field) {
        field.classList.toggle("is-hidden", !enabled);
        if (!enabled) {
          field.querySelectorAll("input, textarea").forEach(function (input) {
            input.value = "";
          });
        }
      });
    }

    function updateRemoveButtons() {
      const count = saleRows().length;
      rows.querySelectorAll("[data-remove-sale-line]").forEach(function (button) {
        button.disabled = count <= 1;
      });
      const paymentCount = paymentLineRows().length;
      paymentRows.querySelectorAll("[data-remove-payment-line]").forEach(function (button) {
        button.disabled = paymentCount <= 1;
      });
    }

    function reindexRows() {
      saleRows().forEach(function (row, index) {
        row.querySelectorAll("[name], [id], label[for]").forEach(function (node) {
          ["name", "id", "for"].forEach(function (attr) {
            const value = node.getAttribute(attr);
            if (value) {
              node.setAttribute(attr, value.replace(/lines-(\d+|__prefix__)-/g, "lines-" + index + "-"));
            }
          });
        });
      });
      totalInput.value = saleRows().length;
    }

    function reindexPaymentRows() {
      paymentLineRows().forEach(function (row, index) {
        row.querySelectorAll("[name], [id], label[for]").forEach(function (node) {
          ["name", "id", "for"].forEach(function (attr) {
            const value = node.getAttribute(attr);
            if (value) {
              node.setAttribute(attr, value.replace(/payments-(\d+|__prefix__)-/g, "payments-" + index + "-"));
            }
          });
        });
      });
      paymentTotalInput.value = paymentLineRows().length;
    }

    function updateTotals() {
      let subtotal = 0;
      saleRows().forEach(function (row) {
        const total = rowTotal(row);
        subtotal += total;
        const target = row.querySelector("[data-line-total]");
        if (target) {
          target.textContent = money(total);
        }
        updateAlterationFields(row);
      });

      let paid = 0;
      let changeDue = 0;
      paymentLineRows().forEach(function (row) {
        const preview = updatePaymentFields(row);
        paid += preview.amount;
        changeDue += preview.change;
      });
      const balance = Math.max(subtotal - paid, 0);
      form.querySelector("[data-sale-subtotal]").textContent = money(subtotal);
      form.querySelector("[data-sale-paid]").textContent = money(paid);
      form.querySelector("[data-sale-change]").textContent = money(changeDue);
      form.querySelector("[data-sale-balance]").textContent = money(balance);
      updateRemoveButtons();
    }

    form.addEventListener("input", updateTotals);
    form.addEventListener("change", updateTotals);

    form.querySelector("[data-add-sale-line]")?.addEventListener("click", function () {
      const index = Number(totalInput.value);
      rows.insertAdjacentHTML("beforeend", emptyTemplate.innerHTML.replaceAll("__prefix__", index));
      reindexRows();
      updateTotals();
    });

    rows.addEventListener("click", function (event) {
      const button = event.target.closest("[data-remove-sale-line]");
      if (!button || saleRows().length <= 1) {
        return;
      }
      button.closest(".sale-line-row").remove();
      reindexRows();
      updateTotals();
    });

    form.querySelector("[data-add-payment-line]")?.addEventListener("click", function () {
      const index = Number(paymentTotalInput.value);
      paymentRows.insertAdjacentHTML("beforeend", emptyPaymentTemplate.innerHTML.replaceAll("__prefix__", index));
      reindexPaymentRows();
      updateTotals();
    });

    paymentRows.addEventListener("click", function (event) {
      const button = event.target.closest("[data-remove-payment-line]");
      if (!button || paymentLineRows().length <= 1) {
        return;
      }
      button.closest(".payment-line-row").remove();
      reindexPaymentRows();
      updateTotals();
    });

    reindexRows();
    reindexPaymentRows();
    updateTotals();
  }

  document.querySelectorAll("[data-sale-editor]").forEach(initSaleEditor);

  function initSettleForm(form) {
    const balance = Number(form.dataset.settleBalance || 0);
    const paymentRows = form.querySelector("[data-settle-payment-rows]");
    const changeRow = form.querySelector("[data-settle-change-row]");
    const changeTarget = form.querySelector("[data-settle-change]");

    function updateSettlePreview() {
      let totalChange = 0;
      let hasCash = false;
      Array.from(paymentRows?.querySelectorAll(".payment-line-row") || []).forEach(function (row) {
        const isCash = (row.querySelector('[name$="-payment_method"]')?.value || "CASH") === "CASH";
        const amount = Number(row.querySelector('[name$="-amount"]')?.value || 0);
        const cashInput = row.querySelector('[name$="-cash_received"]');
        const cashReceived = cashInput && cashInput.value !== "" ? Number(cashInput.value || 0) : amount;
        const change = isCash ? Math.max(cashReceived - amount, 0) : 0;
        hasCash = hasCash || isCash;
        totalChange += change;
        row.querySelectorAll("[data-payment-cash-field]").forEach(function (field) {
          field.classList.toggle("is-hidden", !isCash);
        });
        const target = row.querySelector("[data-payment-change]");
        if (target) {
          target.textContent = money(change);
        }
      });
      if (changeRow) {
        changeRow.classList.toggle("is-hidden", !hasCash);
      }
      if (changeTarget) {
        changeTarget.textContent = money(totalChange);
      }
    }

    form.addEventListener("input", updateSettlePreview);
    form.addEventListener("change", updateSettlePreview);
    updateSettlePreview();
  }

  document.querySelectorAll("[data-settle-form]").forEach(initSettleForm);

  function initCmsBuilder(builder) {
    const outline = builder.querySelector("[data-cms-outline]");
    const previewFrame = builder.querySelector("[data-cms-preview-frame]");
    const openPreview = builder.querySelector("[data-cms-open-preview]");
    const refreshPreview = builder.querySelector("[data-cms-refresh-preview]");
    let activeItem = null;
    let activePointerId = null;
    let startX = 0;
    let startY = 0;
    let didMove = false;

    if (!outline) {
      return;
    }

    function items() {
      return Array.from(outline.querySelectorAll("[data-block-id]"));
    }

    function currentOrder() {
      return items().map(function (item) {
        return item.dataset.blockId;
      });
    }

    function clearDragState() {
      items().forEach(function (item) {
        item.classList.remove("is-drag-over", "is-dragging");
      });
    }

    function shouldPlaceAfter(item, clientY) {
      const box = item.getBoundingClientRect();
      return clientY > box.top + box.height / 2;
    }

    function persistOrder() {
      const body = new URLSearchParams();
      body.set("order", currentOrder().join(","));
      outline.classList.add("is-saving");
      outline.classList.remove("has-save-error");

      fetch(outline.dataset.reorderUrl, {
        method: "POST",
        headers: {
          "X-CSRFToken": outline.dataset.csrf || "",
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: body.toString(),
      })
        .then(function (response) {
          if (!response.ok) {
            throw new Error("No se pudo guardar el orden.");
          }
          return response.json();
        })
        .then(function () {
          items().forEach(function (item, index) {
            const orderValue = String((index + 1) * 10);
            item.querySelectorAll("[data-order-label]").forEach(function (orderLabel) {
              orderLabel.textContent = orderValue;
            });
            builder.querySelectorAll('[data-inspector-for="' + item.dataset.blockId + '"] [data-order-label]').forEach(function (orderLabel) {
              orderLabel.textContent = orderValue;
            });
          });
          reloadPreview();
        })
        .catch(function () {
          outline.classList.add("has-save-error");
        })
        .finally(function () {
          outline.classList.remove("is-saving");
        });
    }

    function selectBlock(item) {
      if (!item) {
        return;
      }
      items().forEach(function (candidate) {
        candidate.classList.toggle("is-active", candidate === item);
      });
      builder.querySelectorAll("[data-inspector-for]").forEach(function (panel) {
        panel.classList.toggle("is-hidden", panel.dataset.inspectorFor !== item.dataset.blockId);
      });
      if (previewFrame && item.dataset.previewUrl) {
        previewFrame.src = item.dataset.previewUrl;
      }
      if (openPreview && item.dataset.previewUrl) {
        openPreview.href = item.dataset.previewUrl;
      }
    }

    function reloadPreview() {
      if (!previewFrame) {
        return;
      }
      const selected = outline.querySelector(".cms-outline-item.is-active") || items()[0];
      if (selected && selected.dataset.previewUrl) {
        previewFrame.src = selected.dataset.previewUrl;
        if (openPreview) {
          openPreview.href = selected.dataset.previewUrl;
        }
      } else {
        previewFrame.src = builder.dataset.previewBase;
      }
    }

    outline.addEventListener("click", function (event) {
      if (event.target.closest("button, a, input, form")) {
        return;
      }
      selectBlock(event.target.closest("[data-block-id]"));
    });

    outline.addEventListener("keydown", function (event) {
      if (event.key !== "Enter" && event.key !== " ") {
        return;
      }
      const item = event.target.closest("[data-block-id]");
      if (item) {
        event.preventDefault();
        selectBlock(item);
      }
    });

    outline.addEventListener("pointerdown", function (event) {
      const handle = event.target.closest("[data-cms-drag-handle]");
      const item = event.target.closest("[data-block-id]");
      if (!handle || !item) {
        return;
      }
      event.preventDefault();
      activeItem = item;
      activePointerId = event.pointerId;
      startX = event.clientX;
      startY = event.clientY;
      didMove = false;
      item.classList.add("is-dragging");
      handle.setPointerCapture(event.pointerId);
    });

    outline.addEventListener("pointermove", function (event) {
      if (!activeItem || event.pointerId !== activePointerId) {
        return;
      }
      event.preventDefault();
      const movedEnough = Math.abs(event.clientX - startX) + Math.abs(event.clientY - startY) > 8;
      if (!movedEnough) {
        return;
      }
      didMove = true;
      clearDragState();
      activeItem.classList.add("is-dragging");

      activeItem.style.visibility = "hidden";
      const elementBelow = document.elementFromPoint(event.clientX, event.clientY);
      activeItem.style.visibility = "";
      const targetItem = elementBelow ? elementBelow.closest("[data-block-id]") : null;
      if (!targetItem || targetItem === activeItem || !outline.contains(targetItem)) {
        return;
      }
      targetItem.classList.add("is-drag-over");
      if (shouldPlaceAfter(targetItem, event.clientY)) {
        outline.insertBefore(activeItem, targetItem.nextSibling);
      } else {
        outline.insertBefore(activeItem, targetItem);
      }
    });

    outline.addEventListener("pointerup", function (event) {
      if (!activeItem || event.pointerId !== activePointerId) {
        return;
      }
      const handle = event.target.closest("[data-cms-drag-handle]");
      if (handle) {
        handle.releasePointerCapture(event.pointerId);
      }
      clearDragState();
      const movedItem = activeItem;
      activeItem = null;
      activePointerId = null;
      if (didMove) {
        selectBlock(movedItem);
        persistOrder();
      }
    });

    outline.addEventListener("pointercancel", function () {
      clearDragState();
      activeItem = null;
      activePointerId = null;
      didMove = false;
    });

    refreshPreview?.addEventListener("click", reloadPreview);
  }

  document.querySelectorAll("[data-cms-builder]").forEach(initCmsBuilder);
})();
