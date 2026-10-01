/**
 * Industrial Fault, Alarm & I/O Status Dashboard
 * Clean, fast, direct viewer for SQL Server database logs and 292 I/O tags.
 */

(function () {
    "use strict";

    // Application State
    const state = {
        activeMainView: "alarms", // 'alarms' | 'io'
        currentPage: 1,
        limit: 50,
        totalRecords: 0,
        autoRefreshSec: 10,
        timerId: null,
        filters: {
            datePreset: "all",
            dateFrom: "",
            dateTo: "",
            search: ""
        },
        // Separate Live I/O View State
        liveIO: {
            data: null,
            filter: "all", // 'all' | 'active' | 'inactive'
            search: ""
        },
        // Modal Snapshot State (Split P1/P2/P3 Layout)
        modalSnapshot: {
            detail: null,
            activeStation: "P1", // 'P1' | 'P2' | 'P3' | 'Common'
            scope: "station",    // 'station' | 'all'
            ioFilter: "all",     // 'all' | 'active' | 'inactive'
            ioSearch: ""
        },
        // Alarm Comparison State (E-Commerce Style)
        compare: {
            selected: new Map(), // Map<id, {id, alarm, station, timestamp, source_table}>
            activeTab: "p1",     // 'p1' | 'p2' | 'p3' | 'io' | 'meta'
            highlightDiffs: true,
            diffsOnly: false,
            search: "",
            loadedSnapshots: []
        }
    };

    // DOM Elements
    const elements = {
        // Status & Controls
        btnPlcStatus: document.getElementById("btnPlcStatus"),
        plcStatusDot: document.getElementById("plcStatusDot"),
        plcStatusText: document.getElementById("plcStatusText"),
        btnSqlStatus: document.getElementById("btnSqlStatus"),
        sqlStatusDot: document.getElementById("sqlStatusDot"),
        sqlStatusText: document.getElementById("sqlStatusText"),
        autoRefreshSelect: document.getElementById("autoRefreshSelect"),
        btnRefresh: document.getElementById("btnRefresh"),
        btnExport: document.getElementById("btnExport"),
        lastUpdatedText: document.getElementById("lastUpdatedText"),

        // Main View Tabs
        btnTabAlarms: document.getElementById("btnTabAlarms"),
        btnTabLiveIO: document.getElementById("btnTabLiveIO"),
        viewAlarmsLog: document.getElementById("viewAlarmsLog"),
        viewIOStatus: document.getElementById("viewIOStatus"),

        // Alarms Filters
        filterDatePreset: document.getElementById("filterDatePreset"),
        customDateGroup: document.getElementById("customDateGroup"),
        filterDateFrom: document.getElementById("filterDateFrom"),
        filterDateTo: document.getElementById("filterDateTo"),
        filterSearch: document.getElementById("filterSearch"),
        btnResetFilters: document.getElementById("btnResetFilters"),

        // Alarms Table & Pagination
        recordCounter: document.getElementById("recordCounter"),
        alarmsTableBody: document.getElementById("alarmsTableBody"),
        btnPrevPage: document.getElementById("btnPrevPage"),
        btnNextPage: document.getElementById("btnNextPage"),
        pageInfo: document.getElementById("pageInfo"),

        // Main Live I/O View Elements
        ioActiveSummary: document.getElementById("ioActiveSummary"),
        pillIOAll: document.getElementById("pillIOAll"),
        pillIOActive: document.getElementById("pillIOActive"),
        pillIOInactive: document.getElementById("pillIOInactive"),
        inputSearchIO: document.getElementById("inputSearchIO"),
        ioStatusTableBody: document.getElementById("ioStatusTableBody"),

        // Modal Elements (P1/P2/P3 Split Layout)
        snapshotModal: document.getElementById("snapshotModal"),
        modalAlarmTitle: document.getElementById("modalAlarmTitle"),
        modalAlarmTimestamp: document.getElementById("modalAlarmTimestamp"),
        modalStationTag: document.getElementById("modalStationTag"),
        modalStationTabs: document.getElementById("modalStationTabs"),
        tabStationP1: document.getElementById("tabStationP1"),
        tabStationP2: document.getElementById("tabStationP2"),
        tabStationP3: document.getElementById("tabStationP3"),
        tabStationCommon: document.getElementById("tabStationCommon"),
        badgeP1Trips: document.getElementById("badgeP1Trips"),
        badgeP2Trips: document.getElementById("badgeP2Trips"),
        badgeP3Trips: document.getElementById("badgeP3Trips"),
        badgeCommonTrips: document.getElementById("badgeCommonTrips"),
        stationParametersContent: document.getElementById("stationParametersContent"),
        modalSearchIO: document.getElementById("modalSearchIO"),
        modalSearchClear: document.getElementById("modalSearchClear"),
        modalPillAll: document.getElementById("modalPillAll"),
        modalPillActive: document.getElementById("modalPillActive"),
        modalPillInactive: document.getElementById("modalPillInactive"),
        countPillAll: document.getElementById("countPillAll"),
        countPillActive: document.getElementById("countPillActive"),
        countPillInactive: document.getElementById("countPillInactive"),
        modalScopeSelect: document.getElementById("modalScopeSelect"),
        modalIOTableBody: document.getElementById("modalIOTableBody"),
        modalFooterSummary: document.getElementById("modalFooterSummary"),
        modalCloseBtn: document.getElementById("modalCloseBtn"),
        modalDismissBtn: document.getElementById("modalDismissBtn"),

        // Alarm Comparison Elements
        compareDock: document.getElementById("compareDock"),
        compareCountText: document.getElementById("compareCountText"),
        compareChipsList: document.getElementById("compareChipsList"),
        btnClearCompare: document.getElementById("btnClearCompare"),
        btnLaunchCompare: document.getElementById("btnLaunchCompare"),
        compareModal: document.getElementById("compareModal"),
        compareModalTitle: document.getElementById("compareModalTitle"),
        compareModalMeta: document.getElementById("compareModalMeta"),
        compareCloseBtn: document.getElementById("compareCloseBtn"),
        compareDismissBtn: document.getElementById("compareDismissBtn"),
        compareStationTabs: document.getElementById("compareStationTabs"),
        cmpTabP1: document.getElementById("cmpTabP1"),
        cmpTabP2: document.getElementById("cmpTabP2"),
        cmpTabP3: document.getElementById("cmpTabP3"),
        cmpTabIO: document.getElementById("cmpTabIO"),
        cmpTabMeta: document.getElementById("cmpTabMeta"),
        chkHighlightDiffs: document.getElementById("chkHighlightDiffs"),
        chkDiffsOnly: document.getElementById("chkDiffsOnly"),
        compareSearchInput: document.getElementById("compareSearchInput"),
        compareMatrixContainer: document.getElementById("compareMatrixContainer"),
        compareFooterStatus: document.getElementById("compareFooterStatus"),

        // Configuration View Elements
        btnTabConfig: document.getElementById("btnTabConfig"),
        viewConfig: document.getElementById("viewConfig"),
        configAlertBox: document.getElementById("configAlertBox"),

        cfgPlcIp: document.getElementById("cfgPlcIp"),
        cfgPlcRack: document.getElementById("cfgPlcRack"),
        cfgPlcSlot: document.getElementById("cfgPlcSlot"),
        cfgPlcDbNumber: document.getElementById("cfgPlcDbNumber"),
        cfgPlcAlarmDb: document.getElementById("cfgPlcAlarmDb"),
        btnTestPLC: document.getElementById("btnTestPLC"),
        plcTestBadge: document.getElementById("plcTestBadge"),

        cfgSqlServer: document.getElementById("cfgSqlServer"),
        cfgSqlDatabase: document.getElementById("cfgSqlDatabase"),
        cfgSqlTrusted: document.getElementById("cfgSqlTrusted"),
        sqlCredentialsGroup: document.getElementById("sqlCredentialsGroup"),
        cfgSqlUser: document.getElementById("cfgSqlUser"),
        cfgSqlPassword: document.getElementById("cfgSqlPassword"),
        btnTestSQL: document.getElementById("btnTestSQL"),
        sqlTestBadge: document.getElementById("sqlTestBadge"),

        cfgMachineId: document.getElementById("cfgMachineId"),
        cfgOperatorName: document.getElementById("cfgOperatorName"),
        cfgWebPort: document.getElementById("cfgWebPort"),
        btnSaveConfig: document.getElementById("btnSaveConfig"),
        btnSaveAndRestart: document.getElementById("btnSaveAndRestart")
    };

    // Initialize
    function init() {
        bindEvents();
        setupAutoRefresh();
        loadAll();
    }

    // Event Bindings
    function bindEvents() {
        // Main Navigation View Tabs
        elements.btnTabAlarms.addEventListener("click", () => switchMainView("alarms"));
        elements.btnTabLiveIO.addEventListener("click", () => switchMainView("io"));
        if (elements.btnTabConfig) {
            elements.btnTabConfig.addEventListener("click", () => switchMainView("config"));
        }

        // Configuration Action Events
        if (elements.cfgSqlTrusted) {
            elements.cfgSqlTrusted.addEventListener("change", toggleSqlCredentials);
        }
        if (elements.btnTestPLC) {
            elements.btnTestPLC.addEventListener("click", handleTestPLC);
        }
        if (elements.btnTestSQL) {
            elements.btnTestSQL.addEventListener("click", handleTestSQL);
        }
        if (elements.btnSaveConfig) {
            elements.btnSaveConfig.addEventListener("click", () => handleSaveConfig(false));
        }
        if (elements.btnSaveAndRestart) {
            elements.btnSaveAndRestart.addEventListener("click", handleSaveAndRestart);
        }

        // Status Indicator Buttons (Click to Test)
        if (elements.btnPlcStatus) {
            elements.btnPlcStatus.addEventListener("click", () => handleTestPlcFromHeader());
        }
        if (elements.btnSqlStatus) {
            elements.btnSqlStatus.addEventListener("click", () => handleTestSqlFromHeader());
        }

        // Refresh & Export
        elements.btnRefresh.addEventListener("click", () => loadAll());
        elements.btnExport.addEventListener("click", () => exportCSV());

        // Auto Refresh
        elements.autoRefreshSelect.addEventListener("change", (e) => {
            state.autoRefreshSec = parseInt(e.target.value, 10);
            setupAutoRefresh();
        });

        // Alarms Date Preset
        elements.filterDatePreset.addEventListener("change", (e) => {
            state.filters.datePreset = e.target.value;
            applyDatePreset(e.target.value);
            state.currentPage = 1;
            loadAlarms();
        });

        // Custom Dates
        elements.filterDateFrom.addEventListener("change", (e) => {
            state.filters.dateFrom = e.target.value;
            state.currentPage = 1;
            loadAlarms();
        });
        elements.filterDateTo.addEventListener("change", (e) => {
            state.filters.dateTo = e.target.value;
            state.currentPage = 1;
            loadAlarms();
        });



        // Search in Alarms
        let alarmSearchDebounce = null;
        elements.filterSearch.addEventListener("input", (e) => {
            clearTimeout(alarmSearchDebounce);
            alarmSearchDebounce = setTimeout(() => {
                state.filters.search = e.target.value.trim();
                state.currentPage = 1;
                loadAlarms();
            }, 250);
        });

        // Reset Filters
        elements.btnResetFilters.addEventListener("click", () => resetFilters());

        // Pagination
        elements.btnPrevPage.addEventListener("click", () => {
            if (state.currentPage > 1) {
                state.currentPage--;
                loadAlarms();
            }
        });
        elements.btnNextPage.addEventListener("click", () => {
            const maxPage = Math.ceil(state.totalRecords / state.limit) || 1;
            if (state.currentPage < maxPage) {
                state.currentPage++;
                loadAlarms();
            }
        });

        // Main Live I/O Filter Pills
        elements.pillIOAll.addEventListener("click", () => setLiveIOFilter("all"));
        elements.pillIOActive.addEventListener("click", () => setLiveIOFilter("active"));
        elements.pillIOInactive.addEventListener("click", () => setLiveIOFilter("inactive"));

        // Main Live I/O Search
        let liveIOSearchDebounce = null;
        elements.inputSearchIO.addEventListener("input", (e) => {
            clearTimeout(liveIOSearchDebounce);
            liveIOSearchDebounce = setTimeout(() => {
                state.liveIO.search = e.target.value.trim().toLowerCase();
                renderLiveIOTable();
            }, 200);
        });

        // Station Tabs (P1, P2, P3, Common)
        if (elements.modalStationTabs) {
            elements.modalStationTabs.addEventListener("click", (e) => {
                const btn = e.target.closest(".station-tab-btn");
                if (btn && btn.dataset.station) {
                    switchModalStation(btn.dataset.station);
                }
            });
        }

        // Modal I/O Filter Pills
        if (elements.modalPillAll) elements.modalPillAll.addEventListener("click", () => setModalIOFilter("all"));
        if (elements.modalPillActive) elements.modalPillActive.addEventListener("click", () => setModalIOFilter("active"));
        if (elements.modalPillInactive) elements.modalPillInactive.addEventListener("click", () => setModalIOFilter("inactive"));

        // Modal Scope Select (This Press Only vs All 292 Tags)
        if (elements.modalScopeSelect) {
            elements.modalScopeSelect.addEventListener("change", (e) => {
                state.modalSnapshot.scope = e.target.value;
                renderRightIOTable();
            });
        }

        // Modal Search Input with debounce & clear button
        let modalIOSearchDebounce = null;
        if (elements.modalSearchIO) {
            elements.modalSearchIO.addEventListener("input", (e) => {
                clearTimeout(modalIOSearchDebounce);
                const val = e.target.value;
                if (elements.modalSearchClear) {
                    elements.modalSearchClear.classList.toggle("hidden", !val);
                }
                modalIOSearchDebounce = setTimeout(() => {
                    state.modalSnapshot.ioSearch = val.trim().toLowerCase();
                    renderRightIOTable();
                }, 180);
            });
        }

        if (elements.modalSearchClear) {
            elements.modalSearchClear.addEventListener("click", () => {
                elements.modalSearchIO.value = "";
                elements.modalSearchClear.classList.add("hidden");
                state.modalSnapshot.ioSearch = "";
                renderRightIOTable();
                elements.modalSearchIO.focus();
            });
        }

        // Modal Dismiss
        if (elements.modalCloseBtn) elements.modalCloseBtn.addEventListener("click", closeModal);
        if (elements.modalDismissBtn) elements.modalDismissBtn.addEventListener("click", closeModal);
        if (elements.snapshotModal) {
            elements.snapshotModal.addEventListener("click", (e) => {
                if (e.target === elements.snapshotModal) closeModal();
            });
        }

        // =====================================================================
        // Alarm Comparison Event Listeners (E-Commerce Style)
        // =====================================================================
        if (elements.alarmsTableBody) {
            elements.alarmsTableBody.addEventListener("change", (e) => {
                const chk = e.target.closest(".alarm-row-checkbox");
                if (chk) {
                    const id = parseInt(chk.dataset.id, 10);
                    const record = state.cachedAlarmRecords?.find(r => r.id === id);
                    if (record) {
                        const success = toggleAlarmSelection(record, chk.checked);
                        if (!success) chk.checked = false;
                    }
                }
            });
        }

        if (elements.btnClearCompare) {
            elements.btnClearCompare.addEventListener("click", clearCompareSelection);
        }

        if (elements.btnLaunchCompare) {
            elements.btnLaunchCompare.addEventListener("click", launchComparison);
        }

        if (elements.compareCloseBtn) elements.compareCloseBtn.addEventListener("click", closeCompareModal);
        if (elements.compareDismissBtn) elements.compareDismissBtn.addEventListener("click", closeCompareModal);
        if (elements.compareModal) {
            elements.compareModal.addEventListener("click", (e) => {
                if (e.target === elements.compareModal) closeCompareModal();
            });
        }

        if (elements.compareStationTabs) {
            elements.compareStationTabs.addEventListener("click", (e) => {
                const btn = e.target.closest(".station-tab-btn");
                if (btn && btn.dataset.tab) {
                    switchCompareTab(btn.dataset.tab);
                }
            });
        }

        if (elements.chkHighlightDiffs) {
            elements.chkHighlightDiffs.addEventListener("change", (e) => {
                state.compare.highlightDiffs = e.target.checked;
                renderComparisonMatrix();
            });
        }

        if (elements.chkDiffsOnly) {
            elements.chkDiffsOnly.addEventListener("change", (e) => {
                state.compare.diffsOnly = e.target.checked;
                renderComparisonMatrix();
            });
        }

        let compareSearchDebounce = null;
        if (elements.compareSearchInput) {
            elements.compareSearchInput.addEventListener("input", (e) => {
                clearTimeout(compareSearchDebounce);
                compareSearchDebounce = setTimeout(() => {
                    state.compare.search = e.target.value.trim().toLowerCase();
                    renderComparisonMatrix();
                }, 180);
            });
        }
    }

    // Switch Main Navigation View
    function switchMainView(view) {
        state.activeMainView = view;
        elements.btnTabAlarms.classList.toggle("active", view === "alarms");
        elements.btnTabLiveIO.classList.toggle("active", view === "io");
        if (elements.btnTabConfig) elements.btnTabConfig.classList.toggle("active", view === "config");

        elements.viewAlarmsLog.classList.toggle("hidden", view !== "alarms");
        elements.viewIOStatus.classList.toggle("hidden", view !== "io");
        if (elements.viewConfig) elements.viewConfig.classList.toggle("hidden", view !== "config");

        if (view === "alarms") {
            loadAlarms();
        } else if (view === "io") {
            loadLiveIO();
        } else if (view === "config") {
            loadConfig();
        }
    }

    function applyDatePreset(preset) {
        const now = new Date();
        if (preset === "all") {
            state.filters.dateFrom = "";
            state.filters.dateTo = "";
            elements.customDateGroup.classList.add("hidden");
        } else if (preset === "today") {
            const start = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0);
            state.filters.dateFrom = formatDateTime(start);
            state.filters.dateTo = "";
            elements.customDateGroup.classList.add("hidden");
        } else if (preset === "yesterday") {
            const yStart = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1, 0, 0, 0);
            const yEnd = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1, 23, 59, 59);
            state.filters.dateFrom = formatDateTime(yStart);
            state.filters.dateTo = formatDateTime(yEnd);
            elements.customDateGroup.classList.add("hidden");
        } else if (preset === "7days") {
            const past7 = new Date(now.getTime() - 7 * 24 * 3600 * 1000);
            state.filters.dateFrom = formatDateTime(past7);
            state.filters.dateTo = "";
            elements.customDateGroup.classList.add("hidden");
        } else if (preset === "custom") {
            elements.customDateGroup.classList.remove("hidden");
        }
    }

    function formatDateTime(d) {
        return d.toISOString().slice(0, 19).replace("T", " ");
    }

    function resetFilters() {
        state.filters.datePreset = "all";
        state.filters.dateFrom = "";
        state.filters.dateTo = "";
        state.filters.search = "";
        state.currentPage = 1;

        elements.filterDatePreset.value = "all";
        elements.customDateGroup.classList.add("hidden");
        elements.filterDateFrom.value = "";
        elements.filterDateTo.value = "";
        elements.filterSearch.value = "";

        loadAlarms();
    }

    function setupAutoRefresh() {
        if (state.timerId) {
            clearInterval(state.timerId);
            state.timerId = null;
        }
        if (state.autoRefreshSec > 0) {
            state.timerId = setInterval(() => loadAll(true), state.autoRefreshSec * 1000);
        }
    }

    async function loadAll(isBackground = false) {
        try {
            await fetchHealth();
            if (state.activeMainView === "alarms") {
                await loadAlarms();
            } else {
                await loadLiveIO();
            }
            const now = new Date();
            elements.lastUpdatedText.textContent = `Updated: ${now.toLocaleTimeString()}`;
        } catch (err) {
            console.error("Dashboard refresh error:", err);
        }
    }

    async function fetchHealth() {
        try {
            const res = await fetch("/api/health");
            const data = await res.json();

            // SQL Server Status
            if (data.sql_connected) {
                if (elements.sqlStatusDot) elements.sqlStatusDot.className = "status-dot connected";
                if (elements.sqlStatusText) elements.sqlStatusText.textContent = "SQL Server: Connected";
                if (elements.btnSqlStatus) elements.btnSqlStatus.title = `SQL Server (${data.sql_server} / ${data.sql_database}) - Connected. Click to re-test.`;
            } else {
                if (elements.sqlStatusDot) elements.sqlStatusDot.className = "status-dot disconnected";
                if (elements.sqlStatusText) elements.sqlStatusText.textContent = "SQL Server: Disconnected";
                if (elements.btnSqlStatus) elements.btnSqlStatus.title = `SQL Server Disconnected: ${data.sql_message || 'Offline'}. Click to re-test.`;
            }

            // Siemens PLC Status
            if (data.plc_connected) {
                if (elements.plcStatusDot) elements.plcStatusDot.className = "status-dot connected";
                if (elements.plcStatusText) elements.plcStatusText.textContent = "PLC: Connected";
                if (elements.btnPlcStatus) elements.btnPlcStatus.title = `Siemens PLC (${data.plc_ip}:102, Rack ${data.plc_rack ?? 0}, Slot ${data.plc_slot ?? 1}) - Connected. Click to re-test.`;
            } else {
                if (elements.plcStatusDot) elements.plcStatusDot.className = "status-dot disconnected";
                if (elements.plcStatusText) elements.plcStatusText.textContent = "PLC: Disconnected";
                if (elements.btnPlcStatus) elements.btnPlcStatus.title = `Siemens PLC Disconnected (${data.plc_ip}:102): ${data.plc_message || 'Unreachable'}. Click to re-test.`;
            }
        } catch (e) {
            if (elements.sqlStatusDot) elements.sqlStatusDot.className = "status-dot disconnected";
            if (elements.sqlStatusText) elements.sqlStatusText.textContent = "Server Offline";
            if (elements.plcStatusDot) elements.plcStatusDot.className = "status-dot disconnected";
            if (elements.plcStatusText) elements.plcStatusText.textContent = "PLC: Offline";
        }
    }
    const loadHealth = fetchHealth;

    async function handleTestPlcFromHeader() {
        if (!elements.btnPlcStatus) return;
        if (elements.plcStatusDot) elements.plcStatusDot.className = "status-dot testing";
        if (elements.plcStatusText) elements.plcStatusText.textContent = "PLC: Testing...";

        try {
            const ip = (elements.cfgPlcIp && elements.cfgPlcIp.value.trim()) || "";
            const rack = parseInt(elements.cfgPlcRack ? elements.cfgPlcRack.value : 0, 10) || 0;
            const slot = parseInt(elements.cfgPlcSlot ? elements.cfgPlcSlot.value : 1, 10) || 1;

            const res = await fetch("/api/config/test-plc", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ plc_ip: ip, plc_rack: rack, plc_slot: slot })
            });
            const json = await res.json();
            if (json.success) {
                if (elements.plcStatusDot) elements.plcStatusDot.className = "status-dot connected";
                if (elements.plcStatusText) elements.plcStatusText.textContent = `PLC: Connected (${json.latency_ms}ms)`;
                elements.btnPlcStatus.title = json.message;
            } else {
                if (elements.plcStatusDot) elements.plcStatusDot.className = "status-dot disconnected";
                if (elements.plcStatusText) elements.plcStatusText.textContent = "PLC: Disconnected";
                elements.btnPlcStatus.title = json.error;
            }
        } catch (err) {
            if (elements.plcStatusDot) elements.plcStatusDot.className = "status-dot disconnected";
            if (elements.plcStatusText) elements.plcStatusText.textContent = "PLC: Error";
            elements.btnPlcStatus.title = err.message;
        }
    }

    async function handleTestSqlFromHeader() {
        if (!elements.btnSqlStatus) return;
        if (elements.sqlStatusDot) elements.sqlStatusDot.className = "status-dot testing";
        if (elements.sqlStatusText) elements.sqlStatusText.textContent = "SQL: Testing...";

        try {
            const server = (elements.cfgSqlServer && elements.cfgSqlServer.value.trim()) || "";
            const database = (elements.cfgSqlDatabase && elements.cfgSqlDatabase.value.trim()) || "";
            const trusted = elements.cfgSqlTrusted ? elements.cfgSqlTrusted.checked : true;
            const user = (elements.cfgSqlUser && elements.cfgSqlUser.value.trim()) || "";
            const password = elements.cfgSqlPassword ? elements.cfgSqlPassword.value : "";

            const res = await fetch("/api/config/test-sql", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    sql_server: server,
                    sql_database: database,
                    sql_trusted_connection: trusted,
                    sql_user: user,
                    sql_password: password
                })
            });
            const json = await res.json();
            if (json.success) {
                if (elements.sqlStatusDot) elements.sqlStatusDot.className = "status-dot connected";
                if (elements.sqlStatusText) elements.sqlStatusText.textContent = "SQL: Connected";
                elements.btnSqlStatus.title = json.message;
            } else {
                if (elements.sqlStatusDot) elements.sqlStatusDot.className = "status-dot disconnected";
                if (elements.sqlStatusText) elements.sqlStatusText.textContent = "SQL: Disconnected";
                elements.btnSqlStatus.title = json.error;
            }
        } catch (err) {
            if (elements.sqlStatusDot) elements.sqlStatusDot.className = "status-dot disconnected";
            if (elements.sqlStatusText) elements.sqlStatusText.textContent = "SQL: Error";
            elements.btnSqlStatus.title = err.message;
        }
    }

    // =========================================================================
    // 1. ALARM LOG TABLE
    // =========================================================================
    async function loadAlarms() {
        const offset = (state.currentPage - 1) * state.limit;
        const queryParams = new URLSearchParams({
            limit: state.limit.toString(),
            offset: offset.toString()
        });

        if (state.filters.dateFrom) queryParams.set("date_from", state.filters.dateFrom);
        if (state.filters.dateTo) queryParams.set("date_to", state.filters.dateTo);

        if (state.filters.search) queryParams.set("search", state.filters.search);

        try {
            const res = await fetch(`/api/alarms?${queryParams.toString()}`);
            const data = await res.json();
            if (data.success) {
                state.totalRecords = data.total;
                renderAlarmsTable(data.records, data.total, offset);
                updatePagination();
            }
        } catch (e) {
            console.error("Failed to load alarm logs:", e);
            elements.alarmsTableBody.innerHTML = '<tr><td colspan="7" class="empty-state">Error loading records from SQL Server.</td></tr>';
        }
    }

    function renderAlarmsTable(records, total, offset) {
        if (elements.recordCounter) {
            elements.recordCounter.textContent = `Total: ${total.toLocaleString()} records`;
        }
        state.cachedAlarmRecords = records || [];

        if (!records || records.length === 0) {
            elements.alarmsTableBody.innerHTML = '<tr><td colspan="8" class="empty-state">No fault alarm records found.</td></tr>';
            return;
        }

        let html = "";
        records.forEach((r, idx) => {
            const stationClass = getStationClass(r.station);
            const isChecked = state.compare.selected.has(r.id) ? "checked" : "";
            html += `
                <tr>
                    <td style="text-align: center;">
                        <input type="checkbox" class="alarm-row-checkbox" data-id="${r.id}" ${isChecked} title="Select to compare">
                    </td>
                    <td class="table-id">${r.id}</td>
                    <td class="table-timestamp">${r.timestamp}</td>
                    <td><span class="station-badge ${stationClass}">${r.station}</span></td>
                    <td class="alarm-text">${escapeHtml(r.alarm)}</td>
                    <td>${escapeHtml(r.operator_name)}</td>
                    <td>${escapeHtml(r.shift)}</td>
                    <td style="text-align: center;">
                        <button class="btn btn-secondary btn-sm" onclick="window.viewSnapshot(${r.id}, '${r.source_table}')" title="View Machine Freeze-Frame">
                            View 
                        </button>
                    </td>
                </tr>
            `;
        });

        elements.alarmsTableBody.innerHTML = html;
    }

    function getStationClass(station) {
        if (!station) return "common";
        if (station.includes("1")) return "p1";
        if (station.includes("2")) return "p2";
        if (station.includes("3")) return "p3";
        if (station.includes("Drive") || station.includes("MPCB")) return "drive";
        return "common";
    }

    function updatePagination() {
        const totalPages = Math.ceil(state.totalRecords / state.limit) || 1;
        elements.pageInfo.textContent = `Page ${state.currentPage} of ${totalPages} (${state.totalRecords.toLocaleString()} records)`;
        elements.btnPrevPage.disabled = (state.currentPage <= 1);
        elements.btnNextPage.disabled = (state.currentPage >= totalPages);
    }

    // =========================================================================
    // 2. MAIN VIEW: SEPARATE LIVE I/O STATUS TABLE
    // =========================================================================
    async function loadLiveIO() {
        try {
            const res = await fetch("/api/io/latest");
            const data = await res.json();
            if (data.success && data.data) {
                state.liveIO.data = data.data;
                renderLiveIOTable();
            }
        } catch (e) {
            elements.ioStatusTableBody.innerHTML = '<tr><td colspan="5" class="empty-state">Failed to load I/O status from SQL Server.</td></tr>';
        }
    }

    function setLiveIOFilter(filterType) {
        state.liveIO.filter = filterType;
        elements.pillIOAll.classList.toggle("active", filterType === "all");
        elements.pillIOActive.classList.toggle("active", filterType === "active");
        elements.pillIOInactive.classList.toggle("active", filterType === "inactive");
        renderLiveIOTable();
    }

    // Helper to determine tag I/O type and formatted address
    function getTagIOInfo(tagOrAddr) {
        if (!tagOrAddr) return { type: "I", addr: "", formatted: "I" };
        let addr = typeof tagOrAddr === "string" ? tagOrAddr : (tagOrAddr.address || "");
        let ioType = typeof tagOrAddr === "object" ? tagOrAddr.io_type : null;

        // Strip any existing brackets
        addr = addr.replace(/[\[\]]/g, "").trim();

        if (!ioType) {
            const uAddr = addr.toUpperCase();
            const uName = (typeof tagOrAddr === "object" ? tagOrAddr.name || "" : "").toUpperCase();
            const uComment = (typeof tagOrAddr === "object" ? tagOrAddr.comment || "" : "").toUpperCase();

            if (uAddr.startsWith("Q") || uName.startsWith("Q ") || uName.startsWith("Q_") ||
                uName.includes("OUTPUT") || uComment.includes("OUTPUT") ||
                uName.includes("SOLENOID") || uName.includes("VALVE COIL") ||
                uName.includes("LAMP") || uName.includes("BUZZER") || uName.includes("SIREN")) {
                ioType = "Q";
            } else {
                ioType = "I";
            }
        }

        // Clean out prefix from addr if it had I or Q already
        if (addr.startsWith("I") || addr.startsWith("Q") || addr.startsWith("i") || addr.startsWith("q")) {
            addr = addr.substring(1).trim();
        }

        return {
            type: ioType,
            addr: addr,
            formatted: `${ioType} ${addr}`
        };
    }

    function renderIOAddressBadge(tagOrAddr) {
        const info = getTagIOInfo(tagOrAddr);
        const badgeClass = info.type === "Q" ? "tag-badge-q" : "tag-badge-i";
        return `<span class="tag-badge ${badgeClass}"><span class="badge-type">${info.type}</span>${escapeHtml(info.addr)}</span>`;
    }

    function renderLiveIOTable() {
        if (!state.liveIO.data || !state.liveIO.data.io_status) return;

        const allTags = state.liveIO.data.io_status;
        const activeCount = state.liveIO.data.active_count || 0;
        const totalCount = state.liveIO.data.total_count || allTags.length;
        elements.ioActiveSummary.textContent = `Active: ${activeCount} / ${totalCount} tags | Snapshot: ${state.liveIO.data.timestamp}`;

        let filtered = allTags;

        // Status Filter
        if (state.liveIO.filter === "active") {
            filtered = filtered.filter(t => t.status === 1);
        } else if (state.liveIO.filter === "inactive") {
            filtered = filtered.filter(t => t.status === 0);
        }

        // Text Search
        if (state.liveIO.search) {
            const q = state.liveIO.search.trim().toLowerCase();
            filtered = filtered.filter(t => {
                const info = getTagIOInfo(t);
                const addr = (t.address || "").toLowerCase();
                const name = (t.name || "").toLowerCase();
                const comment = (t.comment || "").toLowerCase();
                return addr.includes(q) ||
                       info.formatted.toLowerCase().includes(q) ||
                       `${info.type}${info.addr}`.toLowerCase().includes(q) ||
                       name.includes(q) ||
                       comment.includes(q);
            });
        }

        if (filtered.length === 0) {
            elements.ioStatusTableBody.innerHTML = '<tr><td colspan="5" class="empty-state">No matching I/O tags found.</td></tr>';
            return;
        }

        let html = "";
        filtered.forEach((t, idx) => {
            const statusBadge = t.status === 1
                ? '<span class="status-badge-1">1 (ON)</span>'
                : '<span class="status-badge-0">0 (OFF)</span>';

            html += `
                <tr>
                    <td class="table-id">${idx + 1}</td>
                    <td>${renderIOAddressBadge(t)}</td>
                    <td class="tag-name">${escapeHtml(t.name)}</td>
                    <td class="tag-comment">${escapeHtml(t.comment || "-")}</td>
                    <td style="text-align: center;">${statusBadge}</td>
                </tr>
            `;
        });

        elements.ioStatusTableBody.innerHTML = html;
    }

    // =========================================================================
    // 3. MACHINE SNAPSHOT MODAL (P1/P2/P3 SPLIT LAYOUT + LIVE PARAMETERS & I/O)
    // =========================================================================

    // Classify a tag address or name to P1, P2, P3, or Common
    function classifyTagStation(name) {
        if (!name) return "Common";
        const u = name.toUpperCase();
        if (u.startsWith("P1 ") || u.startsWith("P1_") || u.includes(" P1 ") || u.includes("PRESS 1") || u.includes("PRESS-1") || u.includes("PRESS1")) {
            return "P1";
        }
        if (u.startsWith("P2 ") || u.startsWith("P2_") || u.includes(" P2 ") || u.includes("PRESS 2") || u.includes("PRESS-2") || u.includes("PRESS2")) {
            return "P2";
        }
        if (u.startsWith("P3 ") || u.startsWith("P3_") || u.includes(" P3 ") || u.includes("PRESS 3") || u.includes("PRESS-3") || u.includes("PRESS3")) {
            return "P3";
        }
        return "Common";
    }

    window.viewSnapshot = async function (id, sourceTable) {
        elements.snapshotModal.classList.remove("hidden");
        elements.modalAlarmTitle.textContent = `Loading Machine Snapshot (ID #${id})...`;
        elements.modalAlarmTimestamp.textContent = "Please wait...";
        elements.stationParametersContent.innerHTML = '<div class="loading-state">Retrieving press metrics and sensor states...</div>';
        elements.modalIOTableBody.innerHTML = '<tr><td colspan="4" class="empty-state">Loading I/O status...</td></tr>';

        // Reset search field
        if (elements.modalSearchIO) elements.modalSearchIO.value = "";
        if (elements.modalSearchClear) elements.modalSearchClear.classList.add("hidden");
        state.modalSnapshot.ioSearch = "";
        state.modalSnapshot.ioFilter = "all";
        state.modalSnapshot.scope = "station";
        if (elements.modalScopeSelect) elements.modalScopeSelect.value = "station";

        try {
            const res = await fetch(`/api/alarms/${id}?table=${sourceTable}`);
            const data = await res.json();
            if (data.success && data.detail) {
                state.modalSnapshot.detail = data.detail;

                // Auto-detect which station this alarm belongs to
                const stationStr = (data.detail.station || "").toUpperCase();
                const alarmStr = (data.detail.alarm || "").toUpperCase();

                if (stationStr.includes("PRESS 2") || stationStr.includes("P2") || alarmStr.includes("P2")) {
                    state.modalSnapshot.activeStation = "P2";
                } else if (stationStr.includes("PRESS 3") || stationStr.includes("P3") || alarmStr.includes("P3")) {
                    state.modalSnapshot.activeStation = "P3";
                } else if (stationStr.includes("COMMON") || stationStr.includes("DRIVE")) {
                    state.modalSnapshot.activeStation = "Common";
                } else {
                    state.modalSnapshot.activeStation = "P1";
                }

                renderModalSnapshot(data.detail);
            } else {
                elements.stationParametersContent.innerHTML = '<div class="empty-state">Snapshot details not found.</div>';
                elements.modalIOTableBody.innerHTML = '<tr><td colspan="4" class="empty-state">No I/O data found.</td></tr>';
            }
        } catch (e) {
            elements.stationParametersContent.innerHTML = '<div class="empty-state">Failed to load snapshot details.</div>';
            elements.modalIOTableBody.innerHTML = '<tr><td colspan="4" class="empty-state">Error loading I/O data.</td></tr>';
        }
    };

    function renderModalSnapshot(detail) {
        elements.modalAlarmTitle.textContent = `Fault: ${detail.alarm}`;
        elements.modalAlarmTimestamp.textContent = `${detail.timestamp} | ${detail.operator_name} | ${detail.swift}`;
        elements.modalStationTag.textContent = `Station: ${detail.station || "General"}`;

        // Update tab trips badges
        updateStationTabBadges(detail);

        // Switch to detected station
        switchModalStation(state.modalSnapshot.activeStation);
    }

    function updateStationTabBadges(detail) {
        const activeTrips = detail.active_io_trips || [];
        const tripCounts = { P1: 0, P2: 0, P3: 0, Common: 0 };

        activeTrips.forEach(addr => {
            const tag = (detail.io_status || []).find(t => t.address === addr);
            const st = tag ? classifyTagStation(tag.name) : "Common";
            tripCounts[st] = (tripCounts[st] || 0) + 1;
        });

        const setBadge = (el, count) => {
            if (!el) return;
            el.textContent = `${count} ${count === 1 ? "Trip" : "Trips"}`;
            el.classList.toggle("has-trips", count > 0);
        };

        setBadge(elements.badgeP1Trips, tripCounts.P1);
        setBadge(elements.badgeP2Trips, tripCounts.P2);
        setBadge(elements.badgeP3Trips, tripCounts.P3);
        setBadge(elements.badgeCommonTrips, tripCounts.Common);
    }

    function switchModalStation(station) {
        state.modalSnapshot.activeStation = station;

        // Update active class on tab buttons
        const tabMap = {
            P1: elements.tabStationP1,
            P2: elements.tabStationP2,
            P3: elements.tabStationP3,
            Common: elements.tabStationCommon
        };

        Object.keys(tabMap).forEach(key => {
            if (tabMap[key]) {
                tabMap[key].classList.toggle("active", key === station);
            }
        });

        // Render Left Parameters Panel
        renderLeftParametersPanel(station);

        // Render Right I/O List
        renderRightIOTable();

        // Update footer summary
        const stationNames = { P1: "Press 1 (P1)", P2: "Press 2 (P2)", P3: "Press 3 (P3)", Common: "Common & Auxiliary" };
        if (elements.modalFooterSummary) {
            elements.modalFooterSummary.textContent = `Showing ${stationNames[station] || station} Actual Parameters & I/O Signals`;
        }
    }

    function renderLeftParametersPanel(station) {
        const detail = state.modalSnapshot.detail;
        if (!detail) return;

        if (station === "Common") {
            elements.stationParametersContent.innerHTML = `
                <div class="param-group-card" style="--station-accent: #94a3b8;">
                    <div class="param-group-title">COMMON &amp; AUXILIARY SYSTEM</div>
                    <div style="font-size: 12px; color: var(--text-secondary); line-height: 1.6; padding: 4px 0;">
                        Common electrical infrastructure, main pilot pumps, servo drives, cooling circuits, and automation safety light curtains.
                    </div>
                    <div style="font-size: 11px; color: var(--text-muted); margin-top: 8px;">
                        Use the right panel to inspect all 132 common PLC hardware signals.
                    </div>
                </div>
            `;
            return;
        }

        const pressData = detail.press_actuals?.[station] || {};
        const accentColors = { P1: "#38bdf8", P2: "#10b981", P3: "#a855f7" };
        const accent = accentColors[station] || "#38bdf8";

        // Group parameters logically
        const groups = {
            "Pressures & Tonnages": [
                "MAIN RAM PRESSURE",
                "DIECUSHION PRESSURE",
                "DAMPUR PRESSURE",
                "MAIN RAM TONNAGE",
                "DC TONNAGE",
                "PUMP 1 PRESSURE TRANSDUCER",
                "PUMP 2 PRESSURE TRANSDUCER",
                "PUMP 3 PRESSURE TRANSDUCER",
                "PUMP 4 PRESSURE TRANSDUCER",
                "PUMP 5 PRESSURE TRANSDUCER",
                "PUMP 6 PRESSURE TRANSDUCER",
                "PUMP 7 PRESSURE TRANSDUCER",
                "PUMP 8 PRESSURE TRANSDUCER",
                "PUMP 9 PRESSURE TRANSDUCER",
                "MAIN RAM B-LINE PRESSURE TRANSDUCER"
            ],
            "Positions & Stroke": [
                "MAIN RAM POSITION",
                "DIECUSHION POSITION"
            ],
            "Timing & Cycles": [
                "CYCLE TIME",
                "DWELL TIME",
                "PRV.CYCLE TIME"
            ],
            "Production Counters": [
                "CUMM COUNT",
                "MACHINE LIFE COUNT",
                "SHIFT COUNT"
            ],
            "Oil & Temperature": [
                "OIL LVEL LOW",
                "OIL TEMP HIGH"
            ]
        };

        let html = "";
        for (const [groupTitle, keys] of Object.entries(groups)) {
            let rows = "";
            keys.forEach(k => {
                if (k in pressData) {
                    const val = pressData[k];
                    let unit = "";
                    if (k.includes("PRESSURE")) unit = " bar";
                    else if (k.includes("TONNAGE")) unit = " T";
                    else if (k.includes("POSITION")) unit = " mm";
                    else if (k.includes("TIME")) unit = " s";
                    else if (k.includes("TEMP")) unit = " °C";

                    rows += `
                        <div class="param-metric-row">
                            <span class="param-metric-name">${k}</span>
                            <span class="param-metric-value">${val.toFixed(2)}${unit}</span>
                        </div>
                    `;
                }
            });

            if (rows) {
                html += `
                    <div class="param-group-card" style="--station-accent: ${accent};">
                        <div class="param-group-title">${groupTitle}</div>
                        ${rows}
                    </div>
                `;
            }
        }

        elements.stationParametersContent.innerHTML = html || '<div class="empty-state">No parameters recorded for this station.</div>';
    }

    function setModalIOFilter(filterType) {
        state.modalSnapshot.ioFilter = filterType;
        if (elements.modalPillAll) elements.modalPillAll.classList.toggle("active", filterType === "all");
        if (elements.modalPillActive) elements.modalPillActive.classList.toggle("active", filterType === "active");
        if (elements.modalPillInactive) elements.modalPillInactive.classList.toggle("active", filterType === "inactive");
        renderRightIOTable();
    }

    function renderRightIOTable() {
        const detail = state.modalSnapshot.detail;
        if (!detail || !detail.io_status) return;

        const allTags = detail.io_status;
        const currentStation = state.modalSnapshot.activeStation;
        const scope = state.modalSnapshot.scope;

        // Filter by Scope
        let scopeTags = allTags;
        if (scope === "station") {
            if (currentStation === "Common") {
                scopeTags = allTags.filter(t => classifyTagStation(t.name) === "Common");
            } else {
                scopeTags = allTags.filter(t => classifyTagStation(t.name) === currentStation);
            }
        }

        // Update Pill Counts
        const activeCount = scopeTags.filter(t => t.status === 1).length;
        const inactiveCount = scopeTags.filter(t => t.status === 0).length;
        if (elements.countPillAll) elements.countPillAll.textContent = scopeTags.length;
        if (elements.countPillActive) elements.countPillActive.textContent = activeCount;
        if (elements.countPillInactive) elements.countPillInactive.textContent = inactiveCount;

        // Filter by Status Pill
        let filtered = scopeTags;
        if (state.modalSnapshot.ioFilter === "active") {
            filtered = filtered.filter(t => t.status === 1);
        } else if (state.modalSnapshot.ioFilter === "inactive") {
            filtered = filtered.filter(t => t.status === 0);
        }

        // Filter by Search Query
        const q = state.modalSnapshot.ioSearch.trim().toLowerCase();
        if (q) {
            filtered = filtered.filter(t => {
                const info = getTagIOInfo(t);
                const addr = (t.address || "").toLowerCase();
                const name = (t.name || "").toLowerCase();
                const comment = (t.comment || "").toLowerCase();
                return addr.includes(q) ||
                       info.formatted.toLowerCase().includes(q) ||
                       `${info.type}${info.addr}`.toLowerCase().includes(q) ||
                       name.includes(q) ||
                       comment.includes(q);
            });
        }

        if (filtered.length === 0) {
            elements.modalIOTableBody.innerHTML = '<tr><td colspan="4" class="empty-state">No matching I/O tags found.</td></tr>';
            return;
        }

        let html = "";
        filtered.forEach(t => {
            const statusBadge = t.status === 1
                ? '<span class="status-badge-1">1 (ON)</span>'
                : '<span class="status-badge-0">0 (OFF)</span>';

            html += `
                <tr>
                    <td>${renderIOAddressBadge(t)}</td>
                    <td class="tag-name">${escapeHtml(t.name)}</td>
                    <td class="tag-comment">${escapeHtml(t.comment || "-")}</td>
                    <td style="text-align: center;">${statusBadge}</td>
                </tr>
            `;
        });

        elements.modalIOTableBody.innerHTML = html;
    }

    function closeModal() {
        elements.snapshotModal.classList.add("hidden");
    }

    // Export CSV
    async function exportCSV() {
        const queryParams = new URLSearchParams();
        if (state.filters.dateFrom) queryParams.set("date_from", state.filters.dateFrom);
        if (state.filters.dateTo) queryParams.set("date_to", state.filters.dateTo);
        if (state.filters.search) queryParams.set("search", state.filters.search);

        const btn = elements.btnExport;
        const originalHtml = btn ? btn.innerHTML : "";
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '<span class="btn-icon">⏳</span> Exporting...';
        }

        try {
            const res = await fetch(`/api/alarms/export?${queryParams.toString()}`);
            if (!res.ok) {
                throw new Error(`Server returned status ${res.status}`);
            }
            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.style.display = "none";
            a.href = url;
            a.download = `alarms_export_${Date.now()}.csv`;
            document.body.appendChild(a);
            a.click();
            setTimeout(() => {
                try {
                    document.body.removeChild(a);
                    window.URL.revokeObjectURL(url);
                } catch (_) {}
            }, 500);
        } catch (err) {
            console.error("Export error:", err);
            alert("Failed to export alarms CSV: " + err.message);
        } finally {
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = originalHtml;
            }
        }
    }

    function escapeHtml(str) {
        if (!str) return "";
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // ----------------------------------------------------------------------
    // Configuration View Functions
    // ----------------------------------------------------------------------
    async function loadConfig() {
        try {
            const res = await fetch("/api/config");
            const json = await res.json();
            if (json.success && json.config) {
                const c = json.config;
                if (elements.cfgPlcIp) elements.cfgPlcIp.value = c.plc_ip || "";
                if (elements.cfgPlcRack) elements.cfgPlcRack.value = c.plc_rack ?? 0;
                if (elements.cfgPlcSlot) elements.cfgPlcSlot.value = c.plc_slot ?? 1;
                if (elements.cfgPlcDbNumber) elements.cfgPlcDbNumber.value = c.plc_db_number ?? 1000;
                if (elements.cfgPlcAlarmDb) elements.cfgPlcAlarmDb.value = c.plc_alarm_db ?? 101;

                if (elements.cfgSqlServer) elements.cfgSqlServer.value = c.sql_server || "";
                if (elements.cfgSqlDatabase) elements.cfgSqlDatabase.value = c.sql_database || "";
                if (elements.cfgSqlTrusted) {
                    elements.cfgSqlTrusted.checked = !!c.sql_trusted_connection;
                    toggleSqlCredentials();
                }
                if (elements.cfgSqlUser) elements.cfgSqlUser.value = c.sql_user || "";
                if (elements.cfgSqlPassword) elements.cfgSqlPassword.value = c.sql_password || "";

                if (elements.cfgMachineId) elements.cfgMachineId.value = c.machine_id || "";
                if (elements.cfgOperatorName) elements.cfgOperatorName.value = c.operator_name || "";
                if (elements.cfgWebPort) elements.cfgWebPort.value = c.web_port || 5001;
            }
        } catch (err) {
            showConfigAlert("Failed to load settings: " + err.message, "error");
        }
    }

    function toggleSqlCredentials() {
        if (!elements.cfgSqlTrusted || !elements.sqlCredentialsGroup) return;
        if (elements.cfgSqlTrusted.checked) {
            elements.sqlCredentialsGroup.classList.add("hidden");
        } else {
            elements.sqlCredentialsGroup.classList.remove("hidden");
        }
    }

    function showConfigAlert(message, type = "success") {
        if (!elements.configAlertBox) return;
        elements.configAlertBox.className = `config-alert ${type}`;
        elements.configAlertBox.textContent = message;
        elements.configAlertBox.classList.remove("hidden");
        setTimeout(() => {
            if (elements.configAlertBox) elements.configAlertBox.scrollIntoView({ behavior: "smooth", block: "nearest" });
        }, 50);
    }

    async function handleTestPLC() {
        const badge = elements.plcTestBadge;
        const btn = elements.btnTestPLC;
        badge.className = "test-badge testing";
        badge.textContent = "Connecting...";
        badge.classList.remove("hidden");
        btn.disabled = true;

        try {
            const payload = {
                plc_ip: elements.cfgPlcIp.value.trim(),
                plc_rack: parseInt(elements.cfgPlcRack.value, 10) || 0,
                plc_slot: parseInt(elements.cfgPlcSlot.value, 10) || 1
            };
            const res = await fetch("/api/config/test-plc", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const json = await res.json();
            if (json.success) {
                badge.className = "test-badge success";
                badge.textContent = `✓ ${json.message}`;
            } else {
                badge.className = "test-badge error";
                badge.textContent = `✗ ${json.error}`;
            }
        } catch (err) {
            badge.className = "test-badge error";
            badge.textContent = `✗ Error: ${err.message}`;
        } finally {
            btn.disabled = false;
        }
    }

    async function handleTestSQL() {
        const badge = elements.sqlTestBadge;
        const btn = elements.btnTestSQL;
        badge.className = "test-badge testing";
        badge.textContent = "Connecting...";
        badge.classList.remove("hidden");
        btn.disabled = true;

        try {
            const payload = {
                sql_server: elements.cfgSqlServer.value.trim(),
                sql_database: elements.cfgSqlDatabase.value.trim(),
                sql_trusted_connection: elements.cfgSqlTrusted.checked,
                sql_user: elements.cfgSqlUser.value.trim(),
                sql_password: elements.cfgSqlPassword.value
            };
            const res = await fetch("/api/config/test-sql", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const json = await res.json();
            if (json.success) {
                badge.className = "test-badge success";
                badge.textContent = `✓ ${json.message}`;
            } else {
                badge.className = "test-badge error";
                badge.textContent = `✗ ${json.error}`;
            }
        } catch (err) {
            badge.className = "test-badge error";
            badge.textContent = `✗ Error: ${err.message}`;
        } finally {
            btn.disabled = false;
        }
    }

    function collectConfigPayload() {
        return {
            plc_ip: elements.cfgPlcIp.value.trim(),
            plc_rack: parseInt(elements.cfgPlcRack.value, 10) || 0,
            plc_slot: parseInt(elements.cfgPlcSlot.value, 10) || 1,
            plc_db_number: parseInt(elements.cfgPlcDbNumber.value, 10) || 1000,
            plc_alarm_db: parseInt(elements.cfgPlcAlarmDb.value, 10) || 101,
            sql_server: elements.cfgSqlServer.value.trim(),
            sql_database: elements.cfgSqlDatabase.value.trim(),
            sql_trusted_connection: elements.cfgSqlTrusted.checked,
            sql_user: elements.cfgSqlUser.value.trim(),
            sql_password: elements.cfgSqlPassword.value,
            machine_id: elements.cfgMachineId.value.trim(),
            operator_name: elements.cfgOperatorName.value.trim(),
            web_port: parseInt(elements.cfgWebPort ? elements.cfgWebPort.value : 5001, 10) || 5001
        };
    }

    async function handleSaveConfig(silent = false) {
        const btn = elements.btnSaveConfig;
        if (btn) btn.disabled = true;

        try {
            const payload = collectConfigPayload();
            const res = await fetch("/api/config", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const json = await res.json();
            if (json.success) {
                if (!silent) showConfigAlert("✓ Configuration successfully saved to .env file!", "success");
                await fetchHealth();
                return true;
            } else {
                showConfigAlert(`✗ Failed to save: ${json.error}`, "error");
                return false;
            }
        } catch (err) {
            showConfigAlert(`✗ Error saving configuration: ${err.message}`, "error");
            return false;
        } finally {
            if (btn) btn.disabled = false;
        }
    }

    async function handleSaveAndRestart() {
        const btn = elements.btnSaveAndRestart;
        btn.disabled = true;
        showConfigAlert("Saving configuration to .env and restarting background service...", "warning");

        const saved = await handleSaveConfig(true);
        if (!saved) {
            btn.disabled = false;
            return;
        }

        try {
            const res = await fetch("/api/config/restart-service", { method: "POST" });
            const json = await res.json();
            if (json.success) {
                showConfigAlert(`✓ ${json.message}`, "success");
            } else {
                showConfigAlert(`⚠️ Config saved to .env. ${json.error}`, "warning");
            }
        } catch (err) {
            showConfigAlert(`⚠️ Config saved to .env. Notice restarting service: ${err.message}`, "warning");
        } finally {
            btn.disabled = false;
            await fetchHealth();
        }
    }

    // =========================================================================
    // 4. E-COMMERCE STYLE ALARM COMPARISON MODULE
    // =========================================================================

    function toggleAlarmSelection(alarmRecord, isChecked) {
        if (isChecked) {
            if (state.compare.selected.size >= 4) {
                alert("You can compare up to 4 alarms at a time.");
                return false;
            }
            state.compare.selected.set(alarmRecord.id, alarmRecord);
        } else {
            state.compare.selected.delete(alarmRecord.id);
        }
        updateCompareDock();
        return true;
    }

    window.removeCompareId = function (id) {
        state.compare.selected.delete(id);
        updateCompareDock();
        syncTableCheckboxes();
        if (state.compare.loadedSnapshots.length > 0) {
            state.compare.loadedSnapshots = state.compare.loadedSnapshots.filter(s => s.id !== id);
            if (state.compare.loadedSnapshots.length < 2) {
                closeCompareModal();
            } else {
                renderComparisonMatrix();
            }
        }
    };

    function clearCompareSelection() {
        state.compare.selected.clear();
        updateCompareDock();
        syncTableCheckboxes();
    }

    function updateCompareDock() {
        const count = state.compare.selected.size;
        if (!elements.compareDock) return;

        if (count === 0) {
            elements.compareDock.classList.add("hidden");
            return;
        }

        elements.compareDock.classList.remove("hidden");
        if (elements.compareCountText) {
            elements.compareCountText.textContent = `${count} of 4 selected`;
        }

        let chipsHtml = "";
        state.compare.selected.forEach(item => {
            chipsHtml += `
                <div class="compare-chip">
                    <span>#${item.id} - ${escapeHtml(item.station || "General")}</span>
                    <span class="compare-chip-remove" onclick="window.removeCompareId(${item.id})" title="Remove from compare">&times;</span>
                </div>
            `;
        });
        if (elements.compareChipsList) {
            elements.compareChipsList.innerHTML = chipsHtml;
        }
    }

    async function launchComparison() {
        if (state.compare.selected.size < 2) {
            alert("Please select at least 2 alarms to compare.");
            return;
        }

        elements.compareModal.classList.remove("hidden");
        elements.compareMatrixContainer.innerHTML = '<div class="loading-state">Retrieving and aligning machine freeze-frame snapshots...</div>';

        const items = Array.from(state.compare.selected.values());
        try {
            const promises = items.map(item =>
                fetch(`/api/alarms/${item.id}?table=${item.source_table}`)
                    .then(r => r.json())
                    .then(d => d.detail)
            );
            const snapshots = await Promise.all(promises);
            state.compare.loadedSnapshots = snapshots.filter(Boolean);

            if (elements.compareModalMeta) {
                elements.compareModalMeta.textContent = `Comparing ${snapshots.length} machine freeze-frames (${snapshots.map(s => '#' + s.id).join(' vs ')})`;
            }

            // Auto-select tab based on first snapshot station
            const firstStation = (snapshots[0]?.station || "").toLowerCase();
            if (firstStation.includes("2")) state.compare.activeTab = "p2";
            else if (firstStation.includes("3")) state.compare.activeTab = "p3";
            else state.compare.activeTab = "p1";

            updateCompareTabButtons();
            renderComparisonMatrix();
        } catch (e) {
            console.error("Comparison load error:", e);
            elements.compareMatrixContainer.innerHTML = '<div class="empty-state">Failed to retrieve snapshot data for comparison.</div>';
        }
    }

    function switchCompareTab(tab) {
        state.compare.activeTab = tab;
        updateCompareTabButtons();
        renderComparisonMatrix();
    }

    function updateCompareTabButtons() {
        const tabBtns = elements.compareStationTabs?.querySelectorAll(".station-tab-btn") || [];
        tabBtns.forEach(btn => {
            btn.classList.toggle("active", btn.dataset.tab === state.compare.activeTab);
        });
    }

    function closeCompareModal() {
        if (elements.compareModal) {
            elements.compareModal.classList.add("hidden");
        }
    }

    function renderComparisonMatrix() {
        const snapshots = state.compare.loadedSnapshots;
        if (!snapshots || snapshots.length < 2) {
            elements.compareMatrixContainer.innerHTML = '<div class="empty-state">Select at least 2 alarms to view comparison.</div>';
            return;
        }

        const activeTab = state.compare.activeTab;
        const highlight = state.compare.highlightDiffs;
        const diffsOnly = state.compare.diffsOnly;
        const search = state.compare.search;

        // Render header row
        let thCols = '<th class="compare-param-col">Parameter / Metric</th>';
        snapshots.forEach((s, idx) => {
            const isBase = idx === 0;
            const badgeLabel = isBase ? "BASELINE" : `COMPARISON #${idx}`;
            const badgeColor = isBase ? "#38bdf8" : "#10b981";
            thCols += `
                <th class="compare-val-col">
                    <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                        <span style="color: ${badgeColor}; font-weight: 700;">${badgeLabel} (#${s.id})</span>
                        <span class="compare-chip-remove" onclick="window.removeCompareId(${s.id})" title="Remove">&times;</span>
                    </div>
                    <div style="font-size: 11px; color: var(--text-primary); margin-top: 3px;">${escapeHtml(s.alarm)}</div>
                    <div style="font-size: 10px; color: var(--text-muted); font-family: var(--font-mono);">${s.timestamp}</div>
                </th>
            `;
        });

        // Show Delta column if comparing 2 alarms
        const showDelta = (snapshots.length === 2);
        if (showDelta) {
            thCols += '<th class="compare-delta-col">Variance (Δ Delta)</th>';
        }

        let bodyHtml = "";
        if (activeTab === "io") {
            bodyHtml = renderIOComparisonRows(snapshots, highlight, diffsOnly, search, showDelta);
        } else if (activeTab === "meta") {
            bodyHtml = renderMetaComparisonRows(snapshots, highlight, showDelta);
        } else {
            const stationKey = activeTab.toUpperCase(); // 'P1', 'P2', 'P3'
            bodyHtml = renderPressComparisonRows(snapshots, stationKey, highlight, diffsOnly, search, showDelta);
        }

        elements.compareMatrixContainer.innerHTML = `
            <table class="compare-table">
                <thead><tr>${thCols}</tr></thead>
                <tbody>${bodyHtml}</tbody>
            </table>
        `;

        if (elements.compareFooterStatus) {
            elements.compareFooterStatus.textContent = `Comparing ${snapshots.length} alarms | Active Tab: ${activeTab.toUpperCase()}`;
        }
    }

    function renderPressComparisonRows(snapshots, stationKey, highlight, diffsOnly, search, showDelta) {
        const groups = {
            "Pressures & Tonnages": [
                "MAIN RAM PRESSURE",
                "DIECUSHION PRESSURE",
                "DAMPUR PRESSURE",
                "MAIN RAM TONNAGE",
                "DC TONNAGE",
                "PUMP 1 PRESSURE TRANSDUCER",
                "PUMP 2 PRESSURE TRANSDUCER",
                "PUMP 3 PRESSURE TRANSDUCER",
                "PUMP 4 PRESSURE TRANSDUCER",
                "PUMP 5 PRESSURE TRANSDUCER",
                "PUMP 6 PRESSURE TRANSDUCER",
                "PUMP 7 PRESSURE TRANSDUCER",
                "PUMP 8 PRESSURE TRANSDUCER",
                "PUMP 9 PRESSURE TRANSDUCER",
                "MAIN RAM B-LINE PRESSURE TRANSDUCER"
            ],
            "Positions & Stroke": [
                "MAIN RAM POSITION",
                "DIECUSHION POSITION"
            ],
            "Timing & Cycles": [
                "CYCLE TIME",
                "DWELL TIME",
                "PRV.CYCLE TIME"
            ],
            "Production Counters": [
                "CUMM COUNT",
                "MACHINE LIFE COUNT",
                "SHIFT COUNT"
            ],
            "Oil & Temperature": [
                "OIL LVEL LOW",
                "OIL TEMP HIGH"
            ]
        };

        const colSpan = snapshots.length + (showDelta ? 2 : 1);
        let html = "";
        let visibleRowsTotal = 0;

        for (const [groupTitle, keys] of Object.entries(groups)) {
            let groupRows = "";

            keys.forEach(key => {
                if (search && !key.toLowerCase().includes(search)) return;

                // Collect values from all snapshots
                const values = snapshots.map(s => {
                    const pressData = s.press_actuals?.[stationKey] || {};
                    return key in pressData ? pressData[key] : null;
                });

                // Check if key exists in at least one snapshot
                if (values.every(v => v === null)) return;

                // Check difference across all snapshots
                const validVals = values.filter(v => v !== null);
                const hasDiff = validVals.length > 1 && !validVals.every(v => Math.abs(v - validVals[0]) < 0.001);

                if (diffsOnly && !hasDiff) return;

                // Format unit
                let unit = "";
                if (key.includes("PRESSURE")) unit = " bar";
                else if (key.includes("TONNAGE")) unit = " T";
                else if (key.includes("POSITION")) unit = " mm";
                else if (key.includes("TIME")) unit = " s";
                else if (key.includes("TEMP")) unit = " °C";

                // Value cells
                let valCells = "";
                values.forEach(v => {
                    const displayVal = v !== null ? `${v.toFixed(2)}${unit}` : "-";
                    valCells += `<td class="compare-val-col">${displayVal}</td>`;
                });

                // Delta cell
                let deltaCell = "";
                if (showDelta) {
                    const v0 = values[0];
                    const v1 = values[1];
                    if (v0 !== null && v1 !== null) {
                        const diff = v1 - v0;
                        if (Math.abs(diff) < 0.001) {
                            deltaCell = '<td class="compare-delta-col"><span class="delta-badge-match">0.00 (MATCH)</span></td>';
                        } else {
                            const pct = (v0 !== 0) ? ` (${diff > 0 ? "+" : ""}${((diff / v0) * 100).toFixed(1)}%)` : "";
                            const diffSign = diff > 0 ? "+" : "";
                            deltaCell = `<td class="compare-delta-col"><span class="delta-badge-diff">⚠️ ${diffSign}${diff.toFixed(2)}${unit}${pct}</span></td>`;
                        }
                    } else {
                        deltaCell = '<td class="compare-delta-col">-</td>';
                    }
                }

                const rowClass = (hasDiff && highlight) ? "row-diff-highlight" : "";
                groupRows += `
                    <tr class="${rowClass}">
                        <td class="compare-param-col">${key}</td>
                        ${valCells}
                        ${deltaCell}
                    </tr>
                `;
                visibleRowsTotal++;
            });

            if (groupRows) {
                html += `
                    <tr class="compare-category-row">
                        <td colspan="${colSpan}">${groupTitle}</td>
                    </tr>
                    ${groupRows}
                `;
            }
        }

        if (visibleRowsTotal === 0) {
            html = `<tr><td colspan="${colSpan}" class="empty-state">${diffsOnly ? "All parameters match identical values (No differences found)." : "No matching parameters found."}</td></tr>`;
        }

        return html;
    }

    function renderIOComparisonRows(snapshots, highlight, diffsOnly, search, showDelta) {
        const colSpan = snapshots.length + (showDelta ? 2 : 1);
        const tagMap = new Map();

        // Build list of all tags present in snapshots
        snapshots.forEach(s => {
            (s.io_status || []).forEach(t => {
                if (!tagMap.has(t.address)) {
                    tagMap.set(t.address, { address: t.address, name: t.name, comment: t.comment || "-" });
                }
            });
        });

        let rowsHtml = "";
        let visibleCount = 0;
        let diffCount = 0;

        tagMap.forEach((meta, addr) => {
            if (search) {
                const q = search.toLowerCase();
                if (!addr.toLowerCase().includes(q) && !meta.name.toLowerCase().includes(q) && !meta.comment.toLowerCase().includes(q)) {
                    return;
                }
            }

            // Get status for each snapshot
            const statuses = snapshots.map(s => {
                const tag = (s.io_status || []).find(t => t.address === addr);
                return tag ? tag.status : 0;
            });

            const hasDiff = !statuses.every(st => st === statuses[0]);
            if (hasDiff) diffCount++;
            if (diffsOnly && !hasDiff) return;

            // Value cells
            let valCells = "";
            statuses.forEach(st => {
                const badge = st === 1
                    ? '<span class="status-badge-1">1 (ON)</span>'
                    : '<span class="status-badge-0">0 (OFF)</span>';
                valCells += `<td class="compare-val-col">${badge}</td>`;
            });

            // Delta cell
            let deltaCell = "";
            if (showDelta) {
                const s0 = statuses[0];
                const s1 = statuses[1];
                if (s0 === s1) {
                    deltaCell = '<td class="compare-delta-col"><span class="delta-badge-match">MATCH</span></td>';
                } else if (s0 === 0 && s1 === 1) {
                    deltaCell = '<td class="compare-delta-col"><span class="delta-badge-diff">🔴 TRIGGERED HIGH</span></td>';
                } else {
                    deltaCell = '<td class="compare-delta-col"><span class="delta-badge-diff">⚠️ DROPPED LOW</span></td>';
                }
            }

            const rowClass = (hasDiff && highlight) ? "row-diff-highlight" : "";
            rowsHtml += `
                <tr class="${rowClass}">
                    <td class="compare-param-col">
                        ${renderIOAddressBadge({ address: addr, name: meta.name, comment: meta.comment, io_type: meta.io_type })}
                        <div style="font-size: 11px; color: var(--text-primary); margin-top: 2px;">${escapeHtml(meta.name)}</div>
                        <div style="font-size: 10px; color: var(--text-muted);">${escapeHtml(meta.comment)}</div>
                    </td>
                    ${valCells}
                    ${deltaCell}
                </tr>
            `;
            visibleCount++;
        });

        if (visibleCount === 0) {
            return `<tr><td colspan="${colSpan}" class="empty-state">${diffsOnly ? "All 292 digital I/O tags have identical states across these alarms." : "No matching I/O signals."}</td></tr>`;
        }

        return `
            <tr class="compare-category-row">
                <td colspan="${colSpan}">DIGITAL I/O SIGNALS (${diffCount} signals divergent across selected events)</td>
            </tr>
            ${rowsHtml}
        `;
    }

    function renderMetaComparisonRows(snapshots, highlight, showDelta) {
        const colSpan = snapshots.length + (showDelta ? 2 : 1);
        const metaFields = [
            { label: "Alarm ID", get: s => `#${s.id}` },
            { label: "Station Classified", get: s => s.station || "General" },
            { label: "Fault / Alarm Description", get: s => s.alarm || "-" },
            { label: "Timestamp", get: s => s.timestamp || "-" },
            { label: "Operator Name", get: s => s.operator_name || "-" },
            { label: "Shift", get: s => s.swift || s.shift || "-" },
            { label: "Active Tripped Signals Count", get: s => `${(s.active_io_trips || []).length} trips` }
        ];

        let html = `
            <tr class="compare-category-row">
                <td colspan="${colSpan}">EVENT METADATA &amp; TIMELINE</td>
            </tr>
        `;

        metaFields.forEach(field => {
            const vals = snapshots.map(s => field.get(s));
            const hasDiff = !vals.every(v => v === vals[0]);

            let valCells = "";
            vals.forEach(v => {
                valCells += `<td class="compare-val-col">${escapeHtml(v)}</td>`;
            });

            let deltaCell = "";
            if (showDelta) {
                if (field.label === "Timestamp" && snapshots.length === 2) {
                    try {
                        const t0 = new Date(snapshots[0].timestamp).getTime();
                        const t1 = new Date(snapshots[1].timestamp).getTime();
                        const diffSec = Math.round(Math.abs(t1 - t0) / 1000);
                        const mins = Math.floor(diffSec / 60);
                        const secs = diffSec % 60;
                        deltaCell = `<td class="compare-delta-col"><span class="delta-badge-info">Δ ${mins}m ${secs}s</span></td>`;
                    } catch (e) {
                        deltaCell = '<td class="compare-delta-col">-</td>';
                    }
                } else if (hasDiff) {
                    deltaCell = '<td class="compare-delta-col"><span class="delta-badge-diff">DIFFERENT</span></td>';
                } else {
                    deltaCell = '<td class="compare-delta-col"><span class="delta-badge-match">IDENTICAL</span></td>';
                }
            }

            const rowClass = (hasDiff && highlight && field.label !== "Alarm ID") ? "row-diff-highlight" : "";
            html += `
                <tr class="${rowClass}">
                    <td class="compare-param-col">${field.label}</td>
                    ${valCells}
                    ${deltaCell}
                </tr>
            `;
        });

        return html;
    }

    document.addEventListener("DOMContentLoaded", init);
})();
