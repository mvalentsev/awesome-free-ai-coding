"use strict";

// The generated model order and option labels come from index.json/render.py.
var FreeTierModelSort = (function () {
  var PARAM = "model-sort", STORAGE = "freetier:model-sort";
  var names = new Intl.Collator("en", {numeric: true, sensitivity: "base"});

  function order(items, mode, counts, family) {
    family = family || function (item) { return item.family; };
    if (mode === "score") return items.slice();
    return items.slice().sort(function (a, b) {
      var left = family(a), right = family(b);
      if (mode === "providers") {
        var difference = (counts[right] || 0) - (counts[left] || 0);
        if (difference) return difference;
      }
      return names.compare(left, right);
    });
  }

  function controller(data, changed) {
    var config = data.model_sort, controls = [], counts = Object.create(null);
    (data.models || []).forEach(function (model) { counts[model.family] = (model.rows || []).length; });
    function valid(value) { return config.options.some(function (option) { return option.id === value; }); }
    function query() { return new URL(location.href).searchParams.get(PARAM); }
    function stored() { try { return localStorage.getItem(STORAGE); } catch (error) { return null; } }
    var current = valid(query()) ? query() : valid(stored()) ? stored() : config.default;
    if (!valid(query())) {
      var initial = new URL(location.href);
      if (current !== config.default) initial.searchParams.set(PARAM, current);
      else initial.searchParams.delete(PARAM);
      history.replaceState(null, "", initial.pathname + initial.search + initial.hash);
    }
    function save() { try { localStorage.setItem(STORAGE, current); } catch (error) { /* URL state still works. */ } }
    function sync(historyChange) {
      controls.forEach(function (select) { select.value = current; });
      save();
      changed({history: !!historyChange});
    }
    function choose(value) {
      if (!valid(value) || value === current) return;
      current = value;
      var url = new URL(location.href);
      url.searchParams.set(PARAM, current);
      history.pushState(null, "", url.pathname + url.search + url.hash);
      sync(false);
    }
    window.addEventListener("popstate", function () {
      current = valid(query()) ? query() : config.default;
      sync(true);
    });
    document.addEventListener("click", function (event) {
      var anchor = event.target.closest && event.target.closest("a[href]");
      if (!anchor || anchor.getAttribute("href").charAt(0) === "#") return;
      var url = new URL(anchor.href);
      if (url.href.indexOf(data.site + "/") !== 0 || !/\/(?:models\/|providers\/|browse\.html|$)/.test(url.pathname)) return;
      if (current !== config.default) url.searchParams.set(PARAM, current);
      else url.searchParams.delete(PARAM);
      anchor.href = url.href;
    });
    function control(select, before) {
      if (!select) {
        var label = document.createElement("label");
        label.className = "model-sort";
        label.appendChild(document.createTextNode(config.label + " "));
        select = document.createElement("select");
        label.appendChild(select);
        before.parentNode.insertBefore(label, before);
      }
      if (select.parentNode.tagName === "LABEL" && !select.parentNode.firstChild.nodeValue) {
        select.parentNode.insertBefore(document.createTextNode(config.label + " "), select);
      }
      select.setAttribute("aria-label", config.label);
      config.options.forEach(function (item) {
        var option = document.createElement("option");
        option.value = item.id; option.textContent = item.label; select.appendChild(option);
      });
      select.value = current;
      select.addEventListener("change", function () { choose(select.value); });
      controls.push(select);
      return select;
    }
    return {control: control, value: function () { return current; },
      order: function (items, family) { return order(items, current, counts, family); },
      writeState: function (params) { if (current !== config.default) params.set(PARAM, current); }};
  }

  function mount(data) {
    if (!data.model_sort) return;
    var groups = [].map.call(document.querySelectorAll("[data-model-sort-list], [data-model-sort-inline], [data-model-sort-chips]"), function (root) {
      var chips = root.hasAttribute("data-model-sort-chips");
      var items = [].slice.call(chips ? root.querySelectorAll("[data-model-family]") : root.children).filter(function (item) {
        if (!item.dataset.modelFamily) {
          var code = item.querySelector("code");
          if (code) item.dataset.modelFamily = code.textContent.trim();
        }
        return !!item.dataset.modelFamily;
      });
      return {root: root, items: items, chips: chips};
    }).filter(function (group) { return group.items.length >= data.model_sort.minimum; });
    if (!groups.length) return;
    var sorter = controller(data, apply);
    function apply() {
      groups.forEach(function (group) {
        var root = group.root, items = sorter.order(group.items, function (item) { return item.dataset.modelFamily; });
        if (group.chips) {
          var fold = root.querySelector("details.more"), extra = fold && fold.querySelector(".chips");
          items.forEach(function (item, i) {
            if (extra && i >= Number(root.dataset.visible)) extra.appendChild(item);
            else root.insertBefore(item, fold);
          });
        } else if (root.hasAttribute("data-model-sort-inline")) {
          while (root.firstChild) root.removeChild(root.firstChild);
          items.forEach(function (item, i) {
            if (i) root.appendChild(document.createTextNode(", "));
            root.appendChild(item);
          });
        } else { items.forEach(function (item) { root.appendChild(item); }); }
      });
      document.dispatchEvent(new CustomEvent("freetier:model-sort"));
    }
    groups.forEach(function (group) {
      if (group.chips) return;
      sorter.control(null, group.root.closest("table") || group.root.closest("p") || group.root);
    });
    apply();
    return sorter;
  }

  function mountDocument(endpoint, modelIndex) {
    if (modelIndex) {
      var table = document.querySelector(".markdown-body table tbody");
      if (table) table.setAttribute("data-model-sort-list", "");
    }
    if (!document.querySelector("[data-model-sort-list], [data-model-sort-inline]")) return;
    fetch(endpoint, {cache: "no-cache"}).then(function (response) {
      if (!response.ok) throw new Error("Model sort data: HTTP " + response.status);
      return response.json();
    }).then(mount).catch(function (error) { console.error(error); });
  }
  return {order: order, controller: controller, mount: mount, mountDocument: mountDocument};
})();
