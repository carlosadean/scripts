function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('Rubin Report')
    .addItem('1. Gerar Relatório ANUAL (Consolidado)', 'buildAnnualText')
    .addItem('2. Gerar Relatório por QUARTER (Específico)', 'buildQuarterText')
    .addItem('3. Gerar PLANO DE TRABALHO (Next Quarter)', 'buildWorkPlanNextQuarter')
    .addToUi();
}

/**
 * Lê os dados da aba 'Entries' e mapeia para objetos JSON
 */
function readEntries_() {
  var ss = SpreadsheetApp.getActive();
  var sheet = ss.getSheetByName('Entries');
  var data = sheet.getDataRange().getValues();
  var header = data.shift();
  var idx = {};
  for (var i = 0; i < header.length; i++) {
    idx[String(header[i]).trim()] = i;
  }
  var rows = [];
  for (var r = 0; r < data.length; r++) {
    var line = data[r];
    if (!line[idx['Activity / Title']] || !line[idx['FY']]) continue;
    rows.push({
      fy: String(line[idx['FY']] || '').trim(),
      q: String(line[idx['Quarter']] || '').trim(),
      area: String(line[idx['Area']] || '').trim(),
      type: String(line[idx['Type (PQ/UQ)']] || '').trim(),
      title: String(line[idx['Activity / Title']] || '').trim(),
      status: String(line[idx['Status']] || '').trim(),
      desc: String(line[idx['Description (1-2 lines)']] || '').trim()
    });
  }
  return rows;
}

/**
 * OPÇÃO 3: PLANO DE TRABALHO (Work Plan)
 */
function buildWorkPlanNextQuarter() {
  var ui = SpreadsheetApp.getUi();
  var rows = readEntries_();
  var fyTarget = ui.prompt('Work Plan', 'Qual o FY atual?', ui.ButtonSet.OK_CANCEL).getResponseText().trim();
  var qCurrent = ui.prompt('Work Plan', 'Qual o Quarter ATUAL?', ui.ButtonSet.OK_CANCEL).getResponseText().trim();
  
  var qNextMap = { 'Q1': 'Q2', 'Q2': 'Q3', 'Q3': 'Q4', 'Q4': 'Q1' };
  var qNext = qNextMap[qCurrent];
  var groups = {};
  var titlesSeen = {};

  rows.forEach(function(r) {
    var s = r.status.toLowerCase();
    var isCurrentInProgress = (r.fy === fyTarget && r.q === qCurrent && (s.includes('progress') || s === 'ongoing' || s === ''));
    var isNextPlanned = (r.fy === fyTarget && r.q === qNext && (s === '' || s.includes('planned')));

    if ((isCurrentInProgress || isNextPlanned) && !titlesSeen[r.title]) {
      titlesSeen[r.title] = true;
      if (!groups[r.area]) groups[r.area] = [];
      groups[r.area].push("- " + (isCurrentInProgress ? "Continue " : "") + r.title);
    }
  });

  generateSimpleOutput_('WorkPlan_Next_After_' + qCurrent, groups, "PLAN OF WORK FOR THE NEXT QUARTER");
}

/**
 * OPÇÃO 2: RELATÓRIO TRIMESTRAL (Quarterly)
 */
function buildQuarterText() {
  var ui = SpreadsheetApp.getUi();
  var rows = readEntries_();
  var fy = ui.prompt('Quarterly', 'FY?', ui.ButtonSet.OK_CANCEL).getResponseText();
  var q = ui.prompt('Quarterly', 'Quarter?', ui.ButtonSet.OK_CANCEL).getResponseText();
  
  var groups = {};
  rows.filter(function(r) { return r.fy === fy && r.q === q; }).forEach(function(r) {
    if (!groups[r.area]) groups[r.area] = [];
    var block = "**" + r.title + " - " + statusMap(r.status) + "**";
    if (r.desc) block += "\n" + r.desc;
    groups[r.area].push(block);
  });
  generateSimpleOutput_('Quarterly_' + q, groups, "QUARTERLY PROGRESS REPORT - " + q);
}

/**
 * OPÇÃO 1: RELATÓRIO ANUAL (Annual)
 */
function buildAnnualText() {
  var ui = SpreadsheetApp.getUi();
  var rows = readEntries_();
  var fy = ui.prompt('Anual', 'FY?', ui.ButtonSet.OK_CANCEL).getResponseText();
  
  var consolidated = {};
  var qOrder = { 'Q1': 1, 'Q2': 2, 'Q3': 3, 'Q4': 4 };
  rows.filter(function(r) { return r.fy === fy; }).forEach(function(r) {
    if (!consolidated[r.title] || qOrder[r.q] > qOrder[consolidated[r.title].lastQ]) {
      if (!consolidated[r.title]) consolidated[r.title] = { firstQ: r.q };
      consolidated[r.title].lastQ = r.q;
      consolidated[r.title].area = r.area;
      consolidated[r.title].type = r.type;
      consolidated[r.title].title = r.title;
      consolidated[r.title].status = r.status;
      consolidated[r.title].desc = r.desc;
    }
    if (qOrder[r.q] < qOrder[consolidated[r.title].firstQ]) consolidated[r.title].firstQ = r.q;
  });

  var groups = {};
  Object.values(consolidated).forEach(function(it) {
    if (!groups[it.area]) groups[it.area] = [];
    var qTag = it.firstQ === it.lastQ ? it.firstQ : it.firstQ + "-" + it.lastQ;
    var typeTag = (it.type === 'UQ' || it.type === 'Unplanned') ? 'U' : 'P';
    var block = "**[" + typeTag + qTag + "] " + it.title + " - " + statusMap(it.status) + "**";
    if (it.desc) block += "\n" + it.desc;
    groups[it.area].push(block);
  });
  generateSimpleOutput_('Annual_' + fy, groups, "ANNUAL PROGRESS REPORT - " + fy);
}

/**
 * GERA A SAÍDA NAS ABAS COM FORMATAÇÃO SOLICITADA
 */
function generateSimpleOutput_(sheetName, groups, mainTitle) {
  var out = ["# " + mainTitle, ""];
  var areas = Object.keys(groups).sort();
  
  areas.forEach(function(area, index) {
    out.push("## " + area.toUpperCase());
    out.push("");
    
    groups[area].forEach(function(block) { 
      out.push(block); 
      out.push(""); // Adiciona uma linha de espaço entre cada atividade
    });

    if (index < areas.length - 1) {
      out.push(""); // 1 linha de espaço
      out.push(""); // 2 linhas de espaço (antes do separador)
      out.push("---");
      out.push(""); // 1 linha de espaço
      out.push(""); // 2 linhas de espaço (após o separador)
    }
  });
  
  var ss = SpreadsheetApp.getActive();
  var sh = ss.getSheetByName(sheetName) || ss.insertSheet(sheetName);
  sh.clear().getRange("A1").setNumberFormat("@").setValue(out.join("\n"));
  sh.setColumnWidth(1, 800);
}

/**
 * MAPEIA STATUS DA PLANILHA PARA O PADRÃO RUBIN
 */
function statusMap(s) {
  s = (s || "").toLowerCase();
  if (s.includes('done')) return "COMPLETE";
  if (s.includes('postponed')) return "POSTPONED";
  if (s.includes('canceled')) return "CANCELLED";
  return "ONGOING";
}
