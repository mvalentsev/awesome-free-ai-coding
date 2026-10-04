"use strict";

// Match the separators a reader may use while preserving a model's version dot.
function written(text) { return text.replace(/[\s_-]+/g, ""); }
