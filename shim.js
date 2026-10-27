/* Radar Noronha — versão independente (navegador comum). Substitui o ambiente de painel do Claude. */
(function () {
  var IDS = ['viagens', 'fila_diaria', 'situacao_atual', 'programacao', 'frota', 'registros', 'posicoes_ais'];
  var store = {}, calcs = {}, cache = {}, subs = [], params = {};
  try { new URLSearchParams(location.search).forEach(function (v, k) { params[k] = v; }); } catch (e) {}
  var cols = function (d) { return Array.isArray(d) && d.length && typeof d[0] === 'object' ? Object.keys(d[0]) : []; };
  var res = function (status, data, msg) { return { status: status, data: data || [], rows: data || [], columns: cols(data), value: data, message: msg || '', refreshing: false, meta: [] }; };
  IDS.forEach(function (id) { store[id] = res('loading'); });
  function fire() { subs.forEach(function (f) { try { f(); } catch (e) { console.error(e); } }); }
  window.dash = {
    data: function (id) {
      var c = calcs[id];
      if (c) {
        var ins = c.inputs.map(function (i) { return window.dash.data(i); });
        var bad = ins.find(function (x) { return x.status !== 'ok'; });
        if (bad) return res(bad.status === 'loading' ? 'loading' : 'error');
        if (!(id in cache)) { try { cache[id] = c.fn.apply(null, ins.map(function (x) { return x.data; })); } catch (e) { console.error(e); return res('error', [], String(e)); } }
        return res('ok', cache[id]);
      }
      return store[id] || res('missing');
    },
    onData: function (fn) { subs.push(fn); try { fn(); } catch (e) { console.error(e); } },
    calc: function (id, def) { calcs[id] = def; },
    loader: function () {}, refresh: function () { load(); },
    colors: ['#2f6f8f', '#e8650a', '#1a5c2a', '#b7791f', '#7b5ea7', '#c0392b', '#3a8f8a', '#8a8a8a'],
    params: function () { return Object.assign({}, params); },
    setParams: function (p) {
      Object.assign(params, p);
      try { var q = new URLSearchParams(params).toString(); history.replaceState(null, '', location.pathname + (q ? '?' + q : '') + location.hash); } catch (e) {}
      fire();
    },
    resetParams: function () { params = {}; fire(); },
    setLink: function (name) { try { history.replaceState(null, '', location.pathname + location.search + '#' + name); } catch (e) {} },
  };
  function setAll(obj) {
    IDS.forEach(function (id) { store[id] = obj[id] ? res('ok', obj[id]) : res('missing'); });
    cache = {};
    var g = document.getElementById('radar-gerado');
    if (g && obj.meta && obj.meta.gerado_em) g.textContent = obj.meta.gerado_em;
    fire();
  }
  function load() {
    if (window.RADAR_DATA) { setTimeout(function () { setAll(window.RADAR_DATA); }, 0); return; }
    var v = Date.now();
    Promise.all(IDS.concat(['meta']).map(function (id) {
      return fetch('dados/' + id + '.json?v=' + v, { cache: 'no-store' }).then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; });
    })).then(function (arr) { var o = {}; IDS.concat(['meta']).forEach(function (id, i) { o[id] = arr[i]; }); setAll(o); });
  }
  document.addEventListener('DOMContentLoaded', load);
  var t; window.addEventListener('resize', function () { clearTimeout(t); t = setTimeout(fire, 150); });
  if (!window.RADAR_DATA) setInterval(load, 15 * 60 * 1000);
})();
