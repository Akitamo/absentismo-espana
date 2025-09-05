# Base para Instrucciones finales diseño Absentismo

# Criterios ETCL

Los datos para estimar el absentismo surgen de la Encuesta Trimestral del Coste
Laboral (ETCL), que elabora el Instituto Nacional de Estadística (INE). 

Los datos se ofrecen para un agregado que comprende la práctica totalidad de la
economía nacional: industria (que incluye los sectores de las manufacturas, la minería
y la energía), construcción y servicios (de los que solo se excluyen el servicio doméstico
y la actividad de organizaciones y organismos extraterritoriales, como son,
por ejemplo, las embajadas y las delegaciones de la Unión Europea). Es decir que,
como se señaló más arriba, la ETCL comprende el conjunto de la economía nacional
no agropecuaria (se excluye todo el sector primario: agricultura, ganadería, silvicultura
y pesca), con excepción de una fracción marginal de los servicios.

Comprende todas las Cuentas de Cotización, con independencia de su tamaño, incluidas
en el Régimen General y cuya actividad económica esté encuadrada en las
Secciones B a S de la CNAE-09 y en el Régimen Especial de Trabajadores del Mar y
cuya actividad económica es el transporte marítimo (división 50 de la CNAE-09).
3.2. COLECTIVO POBLACIONAL
Dentro de cada cuenta se investiga, de forma agregada, a todos los asalariados por
cuenta ajena asociados a la misma, por los que haya existido la obligación de cotizar al
menos un día durante el mes de referencia, con independencia de su modalidad
contractual y de su jornada de trabajo.
3.3. ÁMBITO GEOGRÁFICO
El ámbito geográfico abarca todo el territorio nacional, con resultados desagregados
por Comunidades Autónomas. La información correspondiente a Ceuta y Melilla se
proporciona conjuntamente con la de Andalucía.
La encuesta no está diseñada para proporcionar información fiable en el ámbito
provincial ni, por tanto, en ámbitos territoriales inferiores a la provincia.
3.4. COBERTURA SECTORIAL
Se investigan las cuentas de cotización cuya actividad económica esté encuadrada en
los tres grandes sectores económicos: Industria, Construcción y Servicios, en con-creto
aquellos centros con actividades económicas comprendidas en las secciones de la B a
la S de la CNAE-09:

El máximo nivel de desagregación de la actividad económica es el nivel de división
CNAE-09. En concreto, se analizan 82 divisiones de actividad.
Quedan excluidas las secciones: Agricultura, ganadería, silvicultura y pesca (A),
Actividades de los hogares como empleadores de personal doméstico (T) y Actividades
de organizaciones y organismos extraterritoriales (U).
3.5. PERIODO DE REFERENCIA
Dado que se pretende investigar la evolución trimestral de los costes laborales
mensuales por unidad de trabajo, se distinguen:
– El periodo de referencia de los resultados es el trimestre natural.

DEFINICIONES:

**4.1. TRABAJADORES**
Se entiende por trabajador a toda persona ligada a la unidad productora mediante un
contrato de trabajo, independientemente de la modalidad de dicho contrato.
Los trabajadores objeto de encuesta son todos los trabajadores asociados a la cuenta
por los que haya existido obligación de cotizar durante al menos un día en el mes de
referencia.
A efectos de cálculo del coste laboral por trabajador, aquellos que han estado dados de
alta en la cuenta durante un periodo de tiempo inferior al mes se contabilizan como la
parte proporcional al tiempo que han estado de alta en dicha cuenta.
Los trabajadores se clasifican según su jornada en:
Trabajadores a tiempo completo: Son aquellos que realizan la jornada habitual de la
empresa en la actividad de que se trate.
Trabajadores a tiempo parcial: Son los que realizan una jornada inferior al de la jornada
considerada como normal o habitual para un trabajador a tiempo completo en la
actividad de que se trate.

# MÉTRICAS BASE:

1. **Horas Pactadas (HP):** horas legalmente establecidas por acuerdo empleador–trabajadores; Son las horas legalmente establecidas por acuerdo verbal, contrato individual o convenio colectivo entre el trabajador y la empresa.
2. **Horas EFECTIVAS (HE): Criterio según ETCL** Son las horas realmente trabajadas incluyendo las horas extraordinarias (HEXT). Se calculan como las horas pactadas (HP) más las horas extraordinarias (HEXT) menos las horas no trabajadas por distintas causas (HNT). 
3. **Horas extras por trabajador (HEXT):** Son todas aquellas que se realizan por encima de la jornada pactada, bien sean por causa de fuerza mayor (horas extraordinarias estructurales) o
voluntarias (horas extraordinarias no estructurales)
4. **Horas no trabajadas (HNT)** por distintas causas**:** son del total de horas pactadas las no trabajadas por cualquier motivo. Se incluyen: 
5. **Horas no trabajadas REMUNERADAS (HNTR). En los ficheros del INE viene con el nombre de Horas no trabajadas y pagadas.** Se desglosan en las siguientes posibles causas:
    1. Horas no trabajadas por vacaciones (HNTRa) - Vacaciones reglamentarias 
    2. Horas no trabajadas por fiestas (HNTRb)
    3. Horas no trabajadas por I.T.  (Incapacidad Temporal) (HNTRc)
    4. Horas no trabajadas por maternidad (adopción, paternidad..) (HNTRd)
    5. Horas no trabajadas  por permisos remunerados  (nupcialidad, natalidad, fallecimiento…) (HNTRd)
    6. Horas no trabajadas por razones técnicas o económicas (HNTRf): Días u horas no trabajadas por razones técnicas, organizativas o de producción: son ceses temporales de la prestación del servicio o de la producción de bienes por parte del trabajador (días de suspensión) o disminuciones de la jornada de trabajo (horas de reducción con o sin Expediente de Regulación de Empleo), con el fin de remontar situaciones de crisis las empresas. 
    7. Horas no trabajadas por compensación horas extras (HNTRg): Descansos como compensación por horas extraordinarias.
    8. Horas no trabajadas  por otras causas (HNTRh) :son horas no trabajadas por motivos no
    imputables al trabajador ni al empresario como falta ocasional del trabajo, rotura de
    máquinas, falta de materias primas, accidentes atmosféricos, interrupción de la
    fuerza motriz u otras causas de fuerza mayor. La ley permite recuperar estas horas
    no trabajadas a razón de una hora diaria, previa comunicación y si no hay acuerdo
    contra-rio. Este componente sólo recoge las horas que no han sido recuperadas y
    que, por tanto, pueden ser consideradas verdaderamente como no trabajadas.
    9. Otras horas no trabajadas y remuneradas (HNTRi): Horas de representación sindical, cumplimiento de un deber inexcusable, asistencia a exámenes y visitas médicas, entre otros conceptos
6. **Horas no trabajadas NO REMUNERADAS (HNTnR). En el fichero del INE viene con el nombre de horas no trabajadas y no pagadas.** Se desglosan en las siguientes posibles causas:
    1. Horas no trabajadas por conflictividad laboral: es el número total de horas perdidas por huelgas independientemente del ámbito local, sectorial o empresarial, o intensidad total o parcial de las mismas. No se contabiliza el tiempo recuperado con posterioridad.
    2. Horas no trabajadas por otras causas: Absentismo; guarda legal; cierre patronal, ….
    En el caso del cierre patronal el empresario cierra el centro de trabajo por causa de un conflicto colectivo, con peligro de violencia o daños, ocupación ilegal del centro o existencia de irregularidades, que impidan el proceso normal de producción.
    La guarda legal es una reducción de la jornada de trabajo para aquellos empleados que lo soliciten, por tener a su cuidado directo a un menor de 6 años o a un disminuido físico o psíquico que no trabaje.

# MÉTRICAS CALCULADAS:

1. **Horas Pactadas Efectivas (HPE): UTILIZADAS POR el informe Adecco.** Son las horas pactadas (HP)+ horas extraordinarias (HEXT) - horas no trabajadas por vacaciones (HNTRa) y festivos (HNTRb) - Horas no trabajadas por razones técnicas o económicas (HNTRf). Este concepto representa las horas realmente disponibles para el trabajo.
2. **Horas no trabajadas por motivos ocasionales (HNTmo):** Según el informe Adecco, son horas no trabajadas por motivos ocasionales   (distintos de  vacaciones, días festivos y ERTEs): Incluyen:
    - Horas no trabajadas por I.T.  (Incapacidad Temporal) (HNTRc)
    - Horas no trabajadas por maternidad (adopción, paternidad..) (HNTRd)
    - Horas no trabajadas  por permisos remunerados  (nupcialidad, natalidad, fallecimiento…) (HNTRd)
    - Horas no trabajadas por compensación horas extras (HNTRg):
    - Otras horas no trabajadas y remuneradas (HNTRi):
    - Horas perdidas en el lugar de trabajo
    - Horas no trabajadas por conflictividad laboral
    - Otras horas no trabajadas y remuneradas (HNTRi)
3. **Tasa de Absentismo General_Adecco (TA_ad):** El informe Adecco calcula la tasa de absentismo general con la siguiente formula: HNTmo/HPE. Es decir, las horas no trabajadas por motivos ocasionales entre las horas pactadas efectivas.
4. **Tasa de absentismo por IT_Adecco (TAit_ad):** El informe adecco calcula la tasa de absentismo por IT con la siguiente fórmula: Horas no trabajadas por I.T.  (Incapacidad Temporal) (HNTRc) /Horas Pactadas Efectivas (HPE).
5. **Tasa de Absentismo General_Randstad (TA_rd):** El informe de Randstad calcula la tasa de absentismo general con la siguiente fórmula: (HNT - HNTRa - HNTRb) / HP. Es decir, el numerador es el total de horas no trabajadas, restando los días de vacaciones y fiestas y el denominador es el total de horas pactadas.
6. **Tasa de absentismo por IT_Randstad (TAit_rd):** El informe Randstad calcula la tasa de absentismo por IT con la siguiente fórmula: Horas no trabajadas por I.T.  (Incapacidad Temporal) (HNTRc) /Horas Pactadas (HP).

Nota: Todo el cálculo de las tasas globales de absentismo general y por IT se hace sobre los valores correspondientes a la sección B_S Industria, construcción y servicios (excepto actividades de los hogares como empleadores y de organizaciones y organismos extraterritoriales) y luego se hace el desglose para cada una de las secciones de Industria, construcción y servicios.

# ANÁLISIS VISUALES

**Análisis a Nivel Nacional Agregado**

- **Análisis 1: Evolución Temporal de las Tasas de Absentismo**
    - **Propósito:** Mostrar la tendencia histórica (trimestral y anual) del absentismo para identificar patrones y cambios estructurales.
    - **Lectura mínima**: nivel del trimestre; **variación intertrimestral** (p.p.) y **variación interanual** (%).
    - **Qué explica**: tendencia y aceleración/desaceleración del absentismo.
    - **Implementación:**
        - **Visualización:** Gráfico de líneas con dos series: "Tasa de Absentismo General" y "Tasa de Absentismo por IT".
        - **Cálculos:** Presentar en tabla anexa las variaciones interanuales e intertrimestrales en puntos porcentuales (p.p.).
        
- **Análisis 2: Desglose Causal del Absentismo**
    - **Propósito:** Entender el peso relativo de cada tipo de ausencia (IT, permisos, etc.) sobre el total.
    - **Implementación:**
        - **Visualización:** Gráfico de tarta (pie chart) para el último periodo disponible.
        - **Cálculos:** Mostrar el porcentaje de cada categoría sobre el total de horas de absentismo.

### **3.2. Análisis Geográfico por Comunidad Autónoma**

- **Análisis 3: Ranking y Mapa de Absentismo general y por IT por CC.AA.**
    - **Propósito:** Clasificar las CCAA de mayor a menor tasa de absentismo y ofrecer una visión geográfica de la incidencia.
    - **Visualización:** Generar un **gráfico de barras horizontales** ordenado (ranking) y un **mapa coroplético** de España. Realizar uno para la tasa general y otro para la tasa por IT.
    - **Cálculos:** Etiquetar cada barra/región con su tasa y la variación interanual.
    - **Lectura**: top/bottom; **brecha vs. media nacional**; outliers.
    

### **3.3. Análisis por Sector de Actividad (CNAE)**

- **Análisis 4: Comparativa de Grandes Sectores**
    - **Propósito:** Comparar el nivel de absentismo entre Industria, Construcción y Servicios.
    - **Visualización:** Gráficos de anillos (donuts) o de barras comparativas.
    - **Cálculos:** Mostrar la tasa de cada sector y sus variaciones.
        
        
- **Análisis 5: Ranking de Divisiones de Actividad (Máxima Profundidad)**
    - **Propósito:** Identificar con precisión los subsectores con mayores y menores tasas de absentismo.
    - **Visualización:** Generar cuatro gráficos de barras horizontales: Top 10 con mayor/menor absentismo general, y Top 10 con mayor/menor absentismo por IT.
        
        
- **Análisis 6: Ranking de Evolución por División de Actividad**
    - **Propósito:** Identificar los subsectores donde el absentismo está creciendo o decreciendo más rápidamente.
    - **Visualización:** Generar cuatro tablas/infografías destacando los "Top 10" con mayor crecimiento/reducción interanual para absentismo general y por IT.
    - **Cálculos:** Calcular la variación interanual en p.p. para cada división.

### **3.4. Análisis Cruzado**

- **Análisis 7: Tasa de Absentismo por Gran Sector y por CC.AA.**
    - **Propósito:** Analizar cómo se comporta el absentismo en cada CC.AA. dentro de un gran sector específico.
    - **Visualización:** Generar un conjunto de **mapa y ranking de barras** para cada uno de los tres grandes sectores (Industria, Construcción, Servicios).
        
        

# **Métrica Ilustrativa Adicional (Cruce con EPA): dejar para más adelante**

- **Métrica:** Estimación de Personas Ausentes (equivalente a jornada completa).
- 
    
    **Propósito:** Traducir el dato porcentual de la tasa a un número absoluto y más tangible para facilitar su comunicación y comprensión del impacto24242424.
    
- **Implementación:**
    - **Cálculo:** `Tasa de Absentismo (calculada desde ETCL) * Población Ocupada (obtenida de la EPA)`
    - **Nota para la IA:** Esta métrica requiere un cruce con una fuente de datos externa a la ETCL: la **Encuesta de Población Activa (EPA)** del INE. El dato de "Población Ocupada" para el trimestre correspondiente deberá ser obtenido de dicha encuesta.