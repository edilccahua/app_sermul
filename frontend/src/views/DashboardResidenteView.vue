<template>
  <div
    class="h-full flex flex-col"
    :style="{ background: 'var(--sapBackgroundColor)' }"
  >
    <!-- ══ Dynamic Page Header ════════════════════════════════════════════════ -->
    <div
      class="px-6 py-4 border-b shrink-0 flex items-center justify-between"
      :style="{ background: 'var(--sapPageHeader_Background, var(--sapGroup_ContentBackground))', borderColor: 'var(--sapList_BorderColor)' }"
    >
      <div class="flex items-center gap-3">
        <span
          class="sap-icon--home text-2xl"
          :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
        />
        <div>
          <h1
            class="text-xl font-bold"
            :style="{ color: 'var(--sapTextColor)' }"
          >
            Panel de Control del Almacén de Herramientas
          </h1>
          <p
            class="text-sm"
            :style="{ color: 'var(--sapContent_LabelColor)' }"
          >
            KPIs en tiempo real · Actualización automática cada 60 s
          </p>
        </div>
      </div>
      <!-- Acciones del header -->
      <div class="flex items-center gap-3">
        <span
          v-if="dashboardStore.lastFetch"
          class="text-xs font-mono"
          :style="{ color: 'var(--sapContent_LabelColor)' }"
        >
          Actualizado: {{ formatHora(dashboardStore.lastFetch) }}
        </span>
        <button
          :disabled="dashboardStore.loading"
          class="flex items-center gap-2 h-8 px-3 text-xs border rounded-sm transition-colors"
          :style="{ background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }"
          @click="dashboardStore.fetchResidente(true)"
        >
          <span :class="['sap-icon--refresh text-xs', dashboardStore.loading ? 'animate-spin' : '']" />
          Actualizar
        </button>
      </div>
    </div>

    <!-- ══ Loading ════════════════════════════════════════════════════════════ -->
    <div
      v-if="dashboardStore.loading && !m"
      class="flex-1 flex items-center justify-center"
    >
      <div class="text-center space-y-3">
        <span
          class="sap-icon--refresh text-4xl animate-spin block"
          :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
        />
        <p
          class="text-sm"
          :style="{ color: 'var(--sapContent_LabelColor)' }"
        >
          Cargando métricas...
        </p>
      </div>
    </div>

    <!-- ══ Error ══════════════════════════════════════════════════════════════ -->
    <div
      v-else-if="dashboardStore.error && !m"
      class="flex-1 flex items-center justify-center p-6"
    >
      <div
        class="max-w-md p-6 rounded-sm border text-center space-y-3"
        :style="{ background: 'var(--sapErrorBackground)', borderColor: 'var(--sapErrorBorderColor)' }"
      >
        <span
          class="sap-icon--message-error text-3xl block"
          :style="{ color: 'var(--sapNegativeTextColor)' }"
        />
        <p
          class="text-sm"
          :style="{ color: 'var(--sapNegativeTextColor)' }"
        >
          {{ dashboardStore.error }}
        </p>
        <button
          class="h-9 px-4 text-sm border rounded-sm"
          :style="{ background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)', borderColor: 'var(--sapButton_BorderColor)' }"
          @click="dashboardStore.fetchResidente(true)"
        >
          Reintentar
        </button>
      </div>
    </div>

    <!-- ══ CONTENIDO PRINCIPAL ════════════════════════════════════════════════ -->
    <div
      v-else-if="m"
      class="flex-1 overflow-y-auto px-5 pb-5"
    >
      <div class="pt-5 space-y-6">
        <!-- ══════════════════════════════════════════════════════════════════════
           SECCIÓN 1 — KPIs GLOBALES
      ══════════════════════════════════════════════════════════════════════════ -->
        <section ref="sectionRef1">
          <!-- Section Header -->
          <div
            class="flex items-center gap-2 px-4 py-2 mb-4 rounded-sm section-header"
            :style="{ background: 'var(--sapList_HeaderBackground)', borderLeft: '3px solid var(--sapButton_Emphasized_Background)' }"
          >
            <span
              class="sap-icon--bar-chart text-base"
              :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
            />
            <h2
              class="text-sm font-semibold"
              :style="{ color: 'var(--sapTextColor)' }"
            >
              KPIs GLOBALES
            </h2>
          </div>

          <!-- Fila 1: 2fr 2fr 1fr -->
          <div
            class="grid grid-cols-1"
            style="grid-template-columns: 2fr 2fr 1fr; gap: 1rem;"
          >
            <!-- ① SATURACIÓN — Donut gauge -->
            <div class="card-ovp flex flex-col">
              <div class="card-header">
                <span
                  class="sap-icon--status-critical"
                  :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
                />
                <p class="card-title">
                  Saturación de Herramientas
                </p>
                <span
                  class="ml-auto text-xs px-2 py-0.5 rounded-sm border font-medium"
                  :style="saturacionStyle"
                >{{
                  saturacionPct }}%</span>
              </div>
              <div class="flex items-center justify-center py-2">
                <div class="w-36 h-36 relative">
                  <Doughnut
                    v-if="saturacionData"
                    :data="saturacionData"
                    :options="saturacionOptions"
                  />
                  <div class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                    <span
                      class="text-2xl font-bold"
                      :style="{ color: saturacionColor }"
                    >{{ saturacionPct }}%</span>
                    <span
                      class="text-xs"
                      :style="{ color: 'var(--sapContent_LabelColor)' }"
                    >En uso</span>
                  </div>
                </div>
              </div>
              <div class="flex justify-around text-xs mt-1">
                <span :style="{ color: 'var(--sapContent_LabelColor)' }">
                  En uso: <strong :style="{ color: 'var(--sapTextColor)' }">{{ estados.En_Uso }}</strong>
                </span>
                <span :style="{ color: 'var(--sapContent_LabelColor)' }">
                  Disponibles: <strong :style="{ color: 'var(--sapTextColor)' }">{{ estados.Disponible }}</strong>
                </span>
              </div>
            </div>

            <!-- ② HERRAMIENTAS POR ESTADO — Doughnut -->
            <div class="card-ovp">
              <div class="card-header">
                <span
                  class="sap-icon--pie-chart"
                  :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
                />
                <p class="card-title">
                  Herramientas por Estado
                </p>
              </div>
              <div class="flex items-center gap-4 py-2">
                <div class="w-40 h-40 shrink-0">
                  <Doughnut
                    v-if="estadosData"
                    :data="estadosData"
                    :options="donutOptions"
                  />
                </div>
                <!-- Leyenda 2 columnas -->
                <div class="grid grid-cols-1 gap-1 text-xs flex-1">
                  <template
                    v-for="(val, key) in estados"
                    :key="key"
                  >
                    <div class="flex items-center gap-1.5">
                      <div
                        class="w-2.5 h-2.5 rounded-full shrink-0"
                        :style="{ background: estadoColor(key), border: '1px solid ' + estadoBorderColor(key) }"
                      />
                      <span :style="{ color: 'var(--sapContent_LabelColor)' }">{{ key.replace('_', ' ') }}:</span>
                      <strong :style="{ color: 'var(--sapTextColor)' }">{{ val }}</strong>
                    </div>
                  </template>
                </div>
              </div>
            </div>

            <!-- ③ PÉRDIDAS ACUMULADAS — KPI numérico -->
            <div class="card-ovp flex flex-col">
              <div
                class="card-header"
                style="align-items: flex-start;"
              >
                <span
                  class="sap-icon--money-bills"
                  :style="{ color: 'var(--sapNegativeTextColor)' }"
                />
                <div>
                  <p class="card-title">
                    Pérdidas Acumuladas
                  </p>
                  <p
                    class="text-xs mt-0.5"
                    :style="{ color: 'var(--sapContent_LabelColor)' }"
                  >
                    Costo total estimado de pérdidas
                  </p>
                </div>
              </div>
              <div class="flex-1 flex flex-col items-center justify-center py-4 space-y-2">
                <p
                  class="text-4xl font-bold"
                  :style="{ color: 'var(--sapNegativeTextColor)' }"
                >
                  S/ {{ formatMoney(m.costo_total_perdidas) }}
                </p>
                <div class="flex items-center gap-3 text-sm">
                  <span
                    class="flex items-center gap-1 px-2 py-0.5 rounded-sm border text-xs font-medium"
                    :style="{ background: 'var(--sapErrorBackground)', color: 'var(--sapNegativeTextColor)', borderColor: 'var(--sapErrorBorderColor)' }"
                  >
                    <span class="sap-icon--decline text-[10px]" />
                    {{ estados.Perdida }} perdidas
                  </span>
                  <span
                    class="flex items-center gap-1 px-2 py-0.5 rounded-sm border text-xs font-medium"
                    :style="{ background: 'var(--sapWarningBackground)', color: 'var(--sapCriticalColor)', borderColor: 'var(--sapWarningBorderColor)' }"
                  >
                    <span class="sap-icon--message-warning text-[10px]" />
                    {{ estados.Malograda }} malogradas
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Fila 2: 4fr 1fr -->
          <div
            class="grid grid-cols-1"
            style="grid-template-columns: 4fr 1fr; gap: 1rem; margin-top: 1rem;"
          >
            <!-- ④ PÉRDIDAS POR PARADA — Bar vertical + Toggle S/ / # items -->
            <div class="card-ovp flex flex-col h-full">
              <div class="card-header">
                <span
                  class="sap-icon--bar-chart"
                  :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
                />
                <p class="card-title">
                  Pérdidas por Parada
                </p>
                <!-- Toggle S/ ↔ #items -->
                <div
                  class="ml-auto flex text-xs border rounded-sm overflow-hidden"
                  :style="{ borderColor: 'var(--sapButton_BorderColor)' }"
                >
                  <button
                    class="px-2 py-0.5 transition-colors"
                    :style="perdidaToggle === 'valor'
                      ? { background: 'var(--sapButton_Emphasized_Background)', color: 'var(--sapButton_Emphasized_TextColor)' }
                      : { background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)' }"
                    @click="perdidaToggle = 'valor'"
                  >
                    S/
                  </button>
                  <button
                    class="px-2 py-0.5 transition-colors"
                    :style="perdidaToggle === 'cantidad'
                      ? { background: 'var(--sapButton_Emphasized_Background)', color: 'var(--sapButton_Emphasized_TextColor)' }
                      : { background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)' }"
                    @click="perdidaToggle = 'cantidad'"
                  >
                    #
                  </button>
                </div>
              </div>
              <div class="w-full flex-1 relative min-h-[16rem] flex flex-col py-2">
                <div class="flex-1 relative">
                  <div class="absolute inset-0">
                    <Bar
                      v-if="perdidasParadaData"
                      :data="perdidasParadaData"
                      :options="vBarOptions"
                    />
                  </div>
                </div>
                <p
                  class="text-[10px] text-center mt-2 shrink-0"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >
                  Últimas 5 paradas con pérdidas
                </p>
              </div>
            </div>

            <!-- ⑤ ALERTAS OPERATIVAS — Message Strips (D-01 fix: icono por nivel) -->
            <div class="card-ovp flex flex-col h-full">
              <div class="card-header">
                <span
                  class="sap-icon--message-warning"
                  :style="{ color: 'var(--sapCriticalColor)' }"
                />
                <p class="card-title">
                  Alertas Operativas
                </p>
                <span
                  v-if="alertas.length"
                  class="ml-auto text-xs px-2 py-0.5 rounded-sm font-bold"
                  :style="{ background: 'var(--sapErrorBackground)', color: 'var(--sapNegativeTextColor)' }"
                >{{
                  alertas.length
                }}</span>
              </div>
              <div class="mt-2 space-y-2 flex-1 overflow-y-auto">
                <!-- D-01 FIX: ícono mapeado por nivel; D-05 FIX: color de texto correcto -->
                <div
                  v-for="(alerta, i) in alertas.slice(0, 5)"
                  :key="i"
                  class="flex items-start gap-2 p-2 rounded-sm border"
                  :style="alertaEstilo(alerta.nivel)"
                >
                  <!-- Ícono correcto por nivel -->
                  <span
                    :class="[alertaIcono(alerta.nivel), 'text-sm shrink-0 mt-0.5']"
                    :style="{ color: alertaColorIcono(alerta.nivel) }"
                  />
                  <p
                    class="text-[11px] leading-relaxed flex-1"
                    :style="{ color: alertaColorTexto(alerta.nivel) }"
                  >
                    {{ alerta.mensaje }}
                  </p>
                </div>
                <div
                  v-if="!alertas.length"
                  class="py-5 text-center"
                >
                  <span
                    class="sap-icon--accept text-2xl block mb-1"
                    :style="{ color: 'var(--sapPositiveTextColor)' }"
                  />
                  <p
                    class="text-xs"
                    :style="{ color: 'var(--sapContent_LabelColor)' }"
                  >
                    Sin alertas activas
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- ══════════════════════════════════════════════════════════════════════
           SECCIÓN 2 — KPIs POR PARADA
      ══════════════════════════════════════════════════════════════════════════ -->
        <section ref="sectionRef2">
          <!-- Section Header con Selector de Parada -->
          <div
            class="flex items-center gap-3 px-4 py-2 mb-4 rounded-sm flex-wrap section-header"
            :style="{ background: 'var(--sapList_HeaderBackground)', borderLeft: '3px solid var(--sapInformationBorderColor)' }"
          >
            <span
              class="sap-icon--factory text-base"
              :style="{ color: 'var(--sapInformationTextColor)' }"
            />
            <h2
              class="text-sm font-semibold"
              :style="{ color: 'var(--sapTextColor)' }"
            >
              KPIs POR PARADA
            </h2>
            <!-- Dropdown de selección de parada -->
            <select
              v-model.number="paradaSeleccionadaId"
              class="ml-auto h-8 px-3 text-xs border rounded-sm outline-none"
              :style="{
                background: 'var(--sapField_Background)',
                color: 'var(--sapField_TextColor, var(--sapTextColor))',
                borderColor: 'var(--sapField_BorderColor, var(--sapList_BorderColor))',
              }"
              @change="onParadaChange"
            >
              <option :value="null">
                — Todas las paradas —
              </option>
              <option
                v-for="p in paradasActivas"
                :key="p.id"
                :value="p.id"
              >
                {{ p.codigo }} - {{ p.nombre }}
              </option>
            </select>
            <!-- Loading indicator de la sección 2 -->
            <span
              v-if="loadingParada"
              class="sap-icon--refresh text-sm animate-spin"
              :style="{ color: 'var(--sapContent_LabelColor)' }"
            />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- ⑥ TOP GRUPOS POR PARADA — Bar horizontal -->
            <div class="card-ovp flex flex-col h-full">
              <div class="card-header">
                <span
                  class="sap-icon--group"
                  :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
                />
                <p class="card-title">
                  Top Grupos (Herramientas en Uso)
                </p>
              </div>
              <div class="w-full flex-1 relative min-h-[16rem] flex flex-col py-2">
                <div class="flex-1 relative">
                  <div class="absolute inset-0">
                    <Bar
                      v-if="topGruposData"
                      :data="topGruposData"
                      :options="hBarOptions"
                    />
                  </div>
                </div>
                <p
                  v-if="!topGruposData"
                  class="text-xs text-center py-10 shrink-0"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >
                  Sin datos para esta parada
                </p>
              </div>
            </div>

            <!-- ⑦ TOP 10 HERRAMIENTAS MÁS ENTREGADAS -->
            <div class="card-ovp flex flex-col h-full">
              <div class="card-header">
                <span
                  class="sap-icon--list"
                  :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
                />
                <p class="card-title">
                  Top 10 Herramientas Más Entregadas
                </p>
              </div>
              <div
                class="mt-2 flex-1 overflow-y-auto rounded-sm border"
                :style="{ borderColor: 'var(--sapList_BorderColor)' }"
              >
                <!-- Header de tabla -->
                <div
                  class="grid grid-cols-12 px-3 py-1.5 text-xs font-semibold uppercase tracking-wide border-b"
                  :style="{ background: 'var(--sapList_HeaderBackground)', borderColor: 'var(--sapList_BorderColor)', color: 'var(--sapContent_LabelColor)' }"
                >
                  <span class="col-span-1">#</span>
                  <span class="col-span-4">Código</span>
                  <span class="col-span-5">Herramienta</span>
                  <span class="col-span-2 text-right">Usos</span>
                </div>
                <!-- Filas -->
                <div
                  v-for="(h, i) in (mParada?.herramientas_mas_usadas ?? m.herramientas_mas_usadas ?? []).slice(0, 10)"
                  :key="h.catalogo_id"
                  class="grid grid-cols-12 px-3 py-1.5 text-xs border-b last:border-0 transition-colors hover-sap-selection"
                  :style="{ borderColor: 'var(--sapList_BorderColor)', color: 'var(--sapTextColor)' }"
                >
                  <span
                    class="col-span-1 font-mono"
                    :style="{ color: 'var(--sapContent_LabelColor)' }"
                  >{{ i + 1
                  }}</span>
                  <router-link
                    :to="'/app/herramienta/' + h.catalogo_id"
                    class="col-span-4 font-mono text-[10px] hover:underline truncate"
                    :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
                  >
                    {{
                      h.codigo_interno }}
                  </router-link>
                  <span class="col-span-5 truncate">{{ h.nombre }}</span>
                  <span class="col-span-2 text-right font-semibold">{{ h.veces_usada }}</span>
                </div>
                <p
                  v-if="!(mParada?.herramientas_mas_usadas ?? m.herramientas_mas_usadas)?.length"
                  class="text-xs text-center py-3"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >
                  Sin datos
                </p>
              </div>
            </div>

            <!-- ⑦ TOP GRUPOS CON PÉRDIDAS -->
            <div class="card-ovp flex flex-col h-full">
              <div class="card-header">
                <span
                  class="sap-icon--decline"
                  :style="{ color: 'var(--sapNegativeTextColor)' }"
                />
                <p class="card-title">
                  Top Grupos (Pérdidas)
                </p>
                <!-- Toggle S/ ↔ #items -->
                <div
                  class="ml-auto flex text-xs border rounded-sm overflow-hidden"
                  :style="{ borderColor: 'var(--sapButton_BorderColor)' }"
                >
                  <button
                    class="px-2 py-0.5 transition-colors"
                    :style="perdidasGruposToggle === 'valor'
                      ? { background: 'var(--sapButton_Emphasized_Background)', color: 'var(--sapButton_Emphasized_TextColor)' }
                      : { background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)' }"
                    @click="perdidasGruposToggle = 'valor'"
                  >
                    S/
                  </button>
                  <button
                    class="px-2 py-0.5 transition-colors"
                    :style="perdidasGruposToggle === 'cantidad'
                      ? { background: 'var(--sapButton_Emphasized_Background)', color: 'var(--sapButton_Emphasized_TextColor)' }
                      : { background: 'var(--sapButton_Background)', color: 'var(--sapButton_TextColor)' }"
                    @click="perdidasGruposToggle = 'cantidad'"
                  >
                    #
                  </button>
                </div>
              </div>
              <div
                class="mt-2 flex-1 overflow-y-auto rounded-sm border"
                :style="{ borderColor: 'var(--sapList_BorderColor)' }"
              >
                <div
                  v-for="(g, i) in gruposVerguenza"
                  :key="g.grupo_id"
                  class="flex items-center px-3 py-2 border-b last:border-0 hover-sap-selection transition-colors"
                  :style="{ borderColor: 'var(--sapList_BorderColor)' }"
                >
                  <div
                    class="w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold mr-3 shrink-0"
                    :style="{ background: i === 0 ? 'var(--sapNegativeTextColor)' : 'var(--sapNeutralBackground)', color: i === 0 ? '#fff' : 'var(--sapTextColor)' }"
                  >
                    {{ i + 1 }}
                  </div>
                  <div class="flex-1 min-w-0">
                    <p
                      class="text-xs font-bold truncate"
                      :style="{ color: 'var(--sapTextColor)' }"
                      :title="g.nombre_grupo"
                    >
                      GRUPO {{ g.codigo_grupo }} — {{ g.nombre_grupo }}
                    </p>
                  </div>
                  <div class="text-right shrink-0 ml-2">
                    <p
                      class="text-xs font-bold"
                      :style="{ color: 'var(--sapNegativeTextColor)' }"
                    >
                      {{ perdidasGruposToggle === 'valor' ? 'S/ ' + formatMoney(g.valor_perdido) : g.cantidad_perdida + ' unid.' }}
                    </p>
                  </div>
                </div>
                <p
                  v-if="!gruposVerguenza.length"
                  class="text-xs text-center py-4"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >
                  Ningún grupo registra pérdidas.
                </p>
              </div>
            </div>

            <!-- ⑨ RESERVAS PENDIENTES -->
            <div class="card-ovp flex flex-col h-full">
              <div class="card-header">
                <span
                  class="sap-icon--approvals"
                  :style="{ color: 'var(--sapButton_Emphasized_Background)' }"
                />
                <p class="card-title">
                  Reservas Pendientes
                </p>
                <span
                  v-if="(mParada?.reservas_pendientes ?? m.reservas_pendientes) > 0"
                  class="ml-auto text-xs font-bold px-2 py-0.5 rounded-sm"
                  :style="{ background: 'var(--sapErrorBackground)', color: 'var(--sapNegativeTextColor)' }"
                >{{
                  mParada?.reservas_pendientes ?? m.reservas_pendientes }}</span>
              </div>
              <div
                class="mt-2 flex-1 overflow-y-auto rounded-sm border"
                :style="{ borderColor: 'var(--sapList_BorderColor)' }"
              >
                <div
                  class="grid grid-cols-12 px-3 py-1.5 text-xs font-semibold uppercase tracking-wide border-b"
                  :style="{ background: 'var(--sapList_HeaderBackground)', borderColor: 'var(--sapList_BorderColor)', color: 'var(--sapContent_LabelColor)' }"
                >
                  <span class="col-span-2">ID</span>
                  <span class="col-span-6">Grupo</span>
                  <span class="col-span-4 text-right">Fecha</span>
                </div>
                <div
                  v-for="r in (mParada?.tabla_reservas_pendientes ?? m.tabla_reservas_pendientes ?? [])"
                  :key="r.id"
                  class="grid grid-cols-12 px-3 py-1.5 text-xs border-b last:border-0 transition-colors items-center hover-sap-selection"
                  :style="{ borderColor: 'var(--sapList_BorderColor)', color: 'var(--sapTextColor)' }"
                >
                  <span class="col-span-2 font-mono">#{{ r.id }}</span>
                  <span
                    class="col-span-6 truncate"
                    :title="r.grupo"
                  >{{ r.grupo }}</span>
                  <span
                    class="col-span-4 text-right"
                    :style="{ color: 'var(--sapContent_LabelColor)' }"
                  >
                    {{ r.fecha ? format(new Date(r.fecha), 'dd/MM HH:mm') : '' }}
                  </span>
                </div>
                <p
                  v-if="!(mParada?.tabla_reservas_pendientes ?? m.tabla_reservas_pendientes)?.length"
                  class="text-xs text-center py-3"
                  :style="{ color: 'var(--sapContent_LabelColor)' }"
                >
                  No hay reservas pendientes.
                </p>
              </div>
              <div class="mt-3 text-center">
                <router-link
                  to="/app/almacen/solicitudes"
                  class="inline-flex items-center gap-1.5 h-8 px-4 text-xs border rounded-sm"
                  :style="{
                    background: 'var(--sapButton_Emphasized_Background)',
                    color: 'var(--sapButton_Emphasized_TextColor)',
                  }"
                >
                  <span class="sap-icon--action text-xs" />
                  Ver todas las solicitudes
                </router-link>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useIntersectionObserver } from '@vueuse/core'
import { useThemeStore } from '@/stores/theme'
const themeStore = useThemeStore()

import { Doughnut, Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  ArcElement, BarElement, CategoryScale,
  LinearScale, Tooltip, Legend,
} from 'chart.js'
import { useDashboardStore } from '@/stores/dashboard'
import { api } from '@/api'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

ChartJS.register(ArcElement, BarElement, CategoryScale, LinearScale, Tooltip, Legend)

// ── Stores ────────────────────────────────────────────────────────────────────
const dashboardStore = useDashboardStore()
const m = computed(() => dashboardStore.metricas)

// ── Estado sección 2: KPIs por Parada ────────────────────────────────────────
const paradaSeleccionadaId = ref(null)
const mParada = ref(null)  // métricas filtradas por parada
const loadingParada = ref(false)
const perdidaToggle = ref('valor')  // 'valor' | 'cantidad' para toggle S/ / #
const perdidasGruposToggle = ref('valor') // 'valor' o 'cantidad'

const gruposVerguenza = computed(() => {
  const arr = (mParada.value ?? m.value)?.top_grupos_perdidas ?? []
  if (!arr.length) return []
  
  if (perdidasGruposToggle.value === 'valor') {
    return [...arr].sort((a, b) => b.valor_perdido - a.valor_perdido).slice(0, 5) // Top 5
  } else {
    return [...arr].sort((a, b) => b.cantidad_perdida - a.cantidad_perdida).slice(0, 5) // Top 5
  }
})

// ── Helpers: Leer colores SAP desde CSS (Chart.js no soporta CSS vars) ────────
function sapColor(varName) {
  const isDarkMode = themeStore.isDark // Track organic theme changes from the project's store
  const val = getComputedStyle(document.documentElement).getPropertyValue(varName).trim()

  // Fallback de seguridad contra glitches del Canvas en la carga inicial y colores ausentes
  if (!val) {
    const fallbacks = {
      // Fiori Chart Colors (Pastel, Sólidos y adaptativos)
      '--sapChart_Good': isDarkMode ? '#86d871' : '#61a656',       // Verde Vivo vs Verde Sólido
      '--sapChart_Bad': isDarkMode ? '#ff8888' : '#d32030',        // Rojo Claro vs Rojo Sólido
      '--sapChart_Critical': isDarkMode ? '#ffb45a' : '#e17b24',   // Naranja Vivo vs Naranja
      '--sapChart_Sequence_1': isDarkMode ? '#5ab4ff' : '#0854a0', // Azul Vivo vs Azul
      '--sapChart_Neutral': isDarkMode ? '#b8c4c9' : '#848f94',    // Gris Claro vs Gris

      // Fiori Border Colors (Líneas suaves para barras)
      '--sapPositiveBorderColor': isDarkMode ? '#28a745' : '#107e3e',
      '--sapInformationBorderColor': isDarkMode ? '#4db1ff' : '#0a6ed1',
      '--sapNegativeBorderColor': isDarkMode ? '#ff4b4b' : '#bb0000',
      '--sapCriticalBorderColor': isDarkMode ? '#f58b00' : '#e9730c',
      '--sapNeutralBorderColor': isDarkMode ? '#949494' : '#6a6d70',

      '--sapList_BorderColor': isDarkMode ? '#292d32' : '#e4e4e4',
      '--sapContent_LabelColor': isDarkMode ? '#8a949c' : '#666666'
    }
    return fallbacks[varName] || (isDarkMode ? '#1e2732' : '#f5f6f7')
  }
  return val
}

// ── Paradas activas (del payload global) ─────────────────────────────────────
const paradasActivas = computed(() => m.value?.paradas_activas ?? [])

// Auto-seleccionar última parada activa por defecto
watch(paradasActivas, (paradas) => {
  if (paradas.length && paradaSeleccionadaId.value === null) {
    paradaSeleccionadaId.value = paradas[0].id
    onParadaChange()
  }
}, { immediate: true })

// ── Fetch por parada ──────────────────────────────────────────────────────────
async function onParadaChange() {
  if (!paradaSeleccionadaId.value) {
    mParada.value = null
    return
  }
  loadingParada.value = true
  try {
    const { data } = await api.get('/dashboards/residente', {
      params: { parada_id: paradaSeleccionadaId.value },
    })
    mParada.value = data
  } catch {
    mParada.value = null
  } finally {
    loadingParada.value = false
  }
}

// ── Derivados de métricas: estados de herramientas ───────────────────────────
const estados = computed(() => ({
  Disponible: m.value?.herramientas_disponibles ?? 0,
  En_Uso: m.value?.herramientas_en_uso ?? 0,
  Malograda: m.value?.herramientas_malogradas ?? 0,
  Perdida: m.value?.herramientas_perdidas ?? 0,
}))

// ── CARD 1: Saturación ────────────────────────────────────────────────────────
const saturacionPct = computed(() => {
  const h = estados.value
  const total = h.En_Uso + h.Disponible
  if (!total) return 0
  return Math.round((h.En_Uso / total) * 100)
})

const saturacionColor = computed(() => {
  const pct = saturacionPct.value
  if (pct < 60) return sapColor('--sapChart_Good')
  if (pct < 80) return sapColor('--sapChart_Critical')
  return sapColor('--sapChart_Bad')
})

const saturacionBorderColor = computed(() => {
  const pct = saturacionPct.value
  if (pct < 60) return sapColor('--sapPositiveBorderColor')
  if (pct < 80) return sapColor('--sapCriticalBorderColor')
  return sapColor('--sapNegativeBorderColor')
})

const saturacionStyle = computed(() => {
  const pct = saturacionPct.value
  if (pct < 60) return { background: 'var(--sapSuccessBackground)', color: 'var(--sapPositiveTextColor)', borderColor: 'var(--sapSuccessBorderColor)' }
  if (pct < 80) return { background: 'var(--sapWarningBackground)', color: 'var(--sapCriticalColor)', borderColor: 'var(--sapWarningBorderColor)' }
  return { background: 'var(--sapErrorBackground)', color: 'var(--sapNegativeTextColor)', borderColor: 'var(--sapErrorBorderColor)' }
})

const saturacionData = computed(() => {
  if (!m.value) return null
  const h = estados.value
  return {
    datasets: [{
      data: [h.En_Uso, h.Disponible],
      backgroundColor: [saturacionColor.value, sapColor('--sapChart_Neutral')],
      borderColor: [saturacionBorderColor.value, sapColor('--sapNeutralBorderColor')],
      borderWidth: 0,
    }],
  }
})

const saturacionOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '78%',
  plugins: { legend: { display: false }, tooltip: { enabled: false } },
}

// ── CARD 2: Estados ───────────────────────────────────────────────────────────
function estadoColor(estado) {
  return {
    Disponible: sapColor('--sapChart_Good'),
    En_Uso: sapColor('--sapChart_Sequence_1'),
    Malograda: sapColor('--sapChart_Bad'),
    Perdida: sapColor('--sapChart_Neutral'),
    Mantenimiento: sapColor('--sapChart_Critical'),
  }[estado] ?? sapColor('--sapChart_Neutral')
}

function estadoBorderColor(estado) {
  return {
    Disponible: sapColor('--sapPositiveBorderColor'),
    En_Uso: sapColor('--sapInformationBorderColor'),
    Malograda: sapColor('--sapNegativeBorderColor'),
    Perdida: sapColor('--sapNeutralBorderColor'),
    Mantenimiento: sapColor('--sapCriticalBorderColor'),
  }[estado] ?? sapColor('--sapNeutralBorderColor')
}

const estadosData = computed(() => {
  if (!m.value) return null
  const h = estados.value
  const entries = Object.entries(h).filter(([, v]) => v > 0)
  return {
    labels: entries.map(([k]) => k.replace('_', ' ')),
    datasets: [{
      data: entries.map(([, v]) => v),
      backgroundColor: entries.map(([k]) => estadoColor(k)),
      borderColor: entries.map(([k]) => estadoBorderColor(k)),
      borderWidth: 0,
    }],
  }
})

const donutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  cutout: '60%',
  plugins: {
    legend: { display: false },
    tooltip: { callbacks: { label: (ctx) => ` ${ctx.label}: ${ctx.raw}` } },
  },
}

// ── CARD 4: Pérdidas por Parada (con toggle S/ / #items) ─────────────────────
const perdidasParadaData = computed(() => {
  const paradas = (m.value?.perdidas_por_parada ?? []).slice(-5)
  const esValor = perdidaToggle.value === 'valor'
  return {
    labels: paradas.map((p) => p.codigo_parada),
    datasets: [{
      label: esValor ? 'S/ Pérdidas' : 'Cantidad',
      data: paradas.map((p) => esValor ? p.total_perdido : p.cantidad_perdidas),
      backgroundColor: sapColor('--sapChart_Bad'),
      borderColor: sapColor('--sapNegativeBorderColor'),
      borderWidth: 1,
      borderRadius: 2,
      maxBarThickness: 40,
    }],
  }
})

const vBarOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      callbacks: {
        label: (ctx) => perdidaToggle.value === 'valor'
          ? ` S/ ${ctx.raw.toFixed(2)}`
          : ` ${ctx.raw} items`,
      },
    },
  },
  scales: {
    x: { ticks: { color: sapColor('--sapContent_LabelColor'), font: { size: 10 } }, grid: { display: false } },
    y: {
      ticks: {
        color: sapColor('--sapContent_LabelColor'),
        font: { size: 10 },
        callback: (v) => perdidaToggle.value === 'valor' ? `S/ ${v}` : v,
      },
      grid: { color: sapColor('--sapList_BorderColor') },
    },
  },
}))

// ── CARD 6: Top Grupos ────────────────────────────────────────────────────────
const topGruposData = computed(() => {
  const grupos = (mParada.value ?? m.value)?.top_grupos_herramientas ?? []
  if (!grupos.length) return null
  return {
    labels: grupos.map((g) => g.nombre_grupo),
    datasets: [{
      label: 'En uso',
      data: grupos.map((g) => g.herramientas_en_uso),
      backgroundColor: sapColor('--sapChart_Sequence_1'),
      borderColor: sapColor('--sapInformationBorderColor'),
      borderWidth: 1,
      borderRadius: 2,
      maxBarThickness: 40,
    }],
  }
})

const hBarOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  indexAxis: 'y',
  plugins: {
    legend: { display: false },
    tooltip: { callbacks: { label: (ctx) => ` ${ctx.raw} herramientas` } },
  },
  scales: {
    x: {
      ticks: { color: sapColor('--sapContent_LabelColor'), font: { size: 10 } },
      grid: { color: sapColor('--sapList_BorderColor') },
    },
    y: {
      ticks: { color: sapColor('--sapContent_LabelColor'), font: { size: 10 } },
      grid: { display: false },
    },
  },
}))

// ── ALERTAS (derivadas de KPIs, D-01/D-05 FIX: ícono y color correctos) ──────
const alertas = computed(() => {
  const a = []
  const metricas = m.value
  if (!metricas) return a

  if ((metricas.reservas_pendientes ?? 0) > 0) {
    a.push({ nivel: 'error', mensaje: `${metricas.reservas_pendientes} solicitudes pendientes de aprobación` })
  }
  if ((metricas.pendientes_cierre ?? 0) > 0) {
    a.push({ nivel: 'warning', mensaje: `${metricas.pendientes_cierre} herramientas sin devolver en paradas activas` })
  }
  if ((metricas.epps_por_vencer ?? 0) > 0) {
    a.push({ nivel: 'warning', mensaje: `${metricas.epps_por_vencer} EPPs con certificación próxima a vencer` })
  }
  metricas.paradas_activas?.forEach((p) => {
    a.push({ nivel: 'info', mensaje: `Parada activa: ${p.codigo} - ${p.nombre}` })
  })
  return a
})

// D-01 FIX: Ícono correcto mapeado por nivel (no hardcodeado)
function alertaIcono(nivel) {
  return {
    error: 'sap-icon--message-error',
    warning: 'sap-icon--message-warning',
    success: 'sap-icon--message-success',
    info: 'sap-icon--message-information',
  }[nivel] ?? 'sap-icon--message-information'
}

// D-05 FIX: Color de fondo + borde por nivel
function alertaEstilo(nivel) {
  if (nivel === 'error') return { background: 'var(--sapErrorBackground)', borderColor: 'var(--sapErrorBorderColor)' }
  if (nivel === 'warning') return { background: 'var(--sapWarningBackground)', borderColor: 'var(--sapWarningBorderColor)' }
  if (nivel === 'success') return { background: 'var(--sapSuccessBackground)', borderColor: 'var(--sapSuccessBorderColor)' }
  return { background: 'var(--sapInformationBackground)', borderColor: 'var(--sapInformationBorderColor)' }
}

// D-05 FIX: Color del texto del ícono por nivel (contraste correcto)
function alertaColorIcono(nivel) {
  if (nivel === 'error') return 'var(--sapNegativeColor)'
  if (nivel === 'warning') return 'var(--sapCriticalColor)'
  if (nivel === 'success') return 'var(--sapPositiveColor)'
  return 'var(--sapInformationColor)'
}

// D-05 FIX: Color del texto del mensaje por nivel
function alertaColorTexto(nivel) {
  if (nivel === 'error') return 'var(--sapNegativeTextColor)'
  if (nivel === 'warning') return 'var(--sapCriticalColor)'
  if (nivel === 'success') return 'var(--sapPositiveTextColor)'
  return 'var(--sapInformationTextColor)'
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function formatMoney(val) {
  return (val ?? 0).toLocaleString('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatHora(ts) {
  return format(new Date(ts), 'HH:mm:ss', { locale: es })
}

// ── Sticky headers: refs e IntersectionObserver ────────────────────────────────
const sectionRef1 = ref(null)
const sectionRef2 = ref(null)
const activeSection = ref('globales')

onMounted(() => {
  if (sectionRef1.value) {
    useIntersectionObserver(sectionRef1, ([{ isIntersecting }]) => {
      if (isIntersecting) activeSection.value = 'globales'
    }, { threshold: 0 })
  }
  if (sectionRef2.value) {
    useIntersectionObserver(sectionRef2, ([{ isIntersecting }]) => {
      if (isIntersecting) activeSection.value = 'porParada'
    }, { threshold: 0 })
  }
})

// ── Auto-refresh cada 60 s ────────────────────────────────────────────────────
let refreshTimer = null
onMounted(async () => {
  await dashboardStore.fetchResidente()
  refreshTimer = setInterval(() => dashboardStore.fetchResidente(), 60_000)
})
onUnmounted(() => clearInterval(refreshTimer))
</script>

<style scoped>
/* ── Sticky section headers ────────────────────────────────────────────────── */
.section-header {
  position: sticky;
  top: 0;
  z-index: 10;
}

/* ── Compact OVP Card ─────────────────────────────────────────────────────── */
.card-ovp {
  padding: 1rem;
  border-radius: 0.125rem;
  border: 1px solid var(--sapList_BorderColor);
  background: var(--sapGroup_ContentBackground);
  box-shadow: var(--sapContent_Shadow0);
}

/* D-04 FIX: align-items: flex-start (no centrado vertical) en card-header */
.card-header {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--sapList_BorderColor);
}

.card-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--sapTextColor);
  line-height: 1.2;
}
</style>
