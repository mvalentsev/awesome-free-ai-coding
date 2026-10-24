"use strict";

// One query contract for the palette and Browse; DOM and rendering stay with each page.
var FreeTierSearch = (function () {
  function fold(text) {
    return (text || "").replace(/[\s\S]/g, function (c) {
      var low = c.toLowerCase(), base = low.normalize("NFD").replace(/[\u0300-\u036f]/g, "");
      return base.length === 1 ? base : low.length === 1 ? low : c;
    });
  }
  function parse(raw, config) {
    var text = " " + fold(raw).replace(/\s+/g, " ") + " ";
    var picked = { section: "", filters: {} };
    function take(words, apply) {
      words.slice().sort(function (a, b) { return b.length - a.length; }).forEach(function (w) {
        var at = text.indexOf(" " + w + " ");
        if (at !== -1) { text = text.slice(0, at) + " " + text.slice(at + w.length + 1); apply(); }
      });
    }
    config.filters.forEach(function (f) { take(f.words, function () { picked.filters[f.id] = true; }); });
    config.sections.forEach(function (sec) { take(sec.words, function () { picked.section = sec.id; }); });
    return { terms: text.split(" ").filter(Boolean), picked: picked };
  }

  function wanted(o, section, filters) {
    if (section && o.section.id !== section) { return false; }
    return Object.keys(filters).every(function (f) { return !filters[f] || o.flags.indexOf(f) !== -1; });
  }

  // Each term has to be somewhere; the best field it is in decides the order.
  // A single letter is the start of a name, not a letter anywhere in a quote.
  function scoreOffer(o, terms) {
    var total = 0;
    for (var i = 0; i < terms.length; i++) {
      var t = terms[i], best = 0;
      if (t.length === 1) {
        best = o.fName.indexOf(t) === 0 ? 12
          : o.fModels.some(function (m) { return m.indexOf(t) === 0; }) ? 6 : 0;
      } else if (o.fName.indexOf(t) === 0) { best = 12; }
      else if (o.fName.indexOf(t) !== -1) { best = 9; }
      else if (o.fModels.some(function (m) { return m.indexOf(t) !== -1; })) { best = 6; }
      else if (o.fWhat.indexOf(t) !== -1) { best = 3; }
      else if (o.fLimits.indexOf(t) !== -1) { best = 1; }
      if (!best) { total = 0; break; }
      total += best;
    }
    return Math.max(total, wholeOffer(o, terms));
  }
  // Terms that spell one name — "Nemotron 3 Ultra", "GLM 5", "Gemma 4 26B" —
  // are read whole as well: a lone digit starts no
  // name on its own, so term by term the name found nothing.
  function wholeOffer(o, terms) {
    var whole = written(terms.join(""));
    if (whole.length < 3) { return 0; }
    if (o.wModels.some(function (m) { return m.indexOf(whole) !== -1; })) { return 6 * terms.length; }
    return o.wWhat.indexOf(whole) !== -1 ? 3 * terms.length
      : o.wLimits.indexOf(whole) !== -1 ? terms.length : 0;
  }
  function squash(text) { return text.replace(/[\s._-]+/g, ""); }
  function prepareOffer(o) {
    o.fName = fold(o.name); o.fModels = (o.models || []).concat(o.ids || []).map(fold);
    o.fWhat = fold([o.what, o.access || ""].concat(Object.values(o.modelAccess || {})).join(" ")); o.fLimits = fold(o.limits);
    o.wModels = o.fModels.map(written); o.wWhat = written(o.fWhat); o.wLimits = written(o.fLimits);
  }
  function prepareModel(m) { m.fFamily = fold(m.family); m.wFamily = written(m.fFamily); }
  function scoreModel(m, terms) {
    var whole = written(terms.join(""));
    if (terms.length > 1 && whole.length > 2 && m.wFamily.indexOf(whole) !== -1) {
      return m.wFamily === whole ? 32 : m.wFamily.indexOf(whole) === 0 ? 20 : 12;
    }
    var total = squash(m.fFamily) === squash(terms.join("")) ? 20 : 0;
    for (var i = 0; i < terms.length; i++) {
      var at = m.fFamily.indexOf(terms[i]);
      if (at === -1 || (terms[i].length === 1 && at !== 0)) { return 0; }
      total += m.fFamily === terms[i] ? 12 : at === 0 ? 8 : 5;
    }
    return total;
  }

  return {fold: fold, parse: parse, wanted: wanted, prepareOffer: prepareOffer,
    prepareModel: prepareModel, scoreOffer: scoreOffer, scoreModel: scoreModel};
})();
