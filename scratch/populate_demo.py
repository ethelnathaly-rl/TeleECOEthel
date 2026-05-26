import sqlite3
import datetime

def populate():
    print("Conectando a evaluaciones.db...")
    conn = sqlite3.connect('evaluaciones.db')
    cursor = conn.cursor()
    
    # 1. Obtener el examen activo
    cursor.execute("SELECT id, nombre, tipo_evaluacion FROM examen WHERE estado='activo' ORDER BY id DESC")
    active_exam = cursor.fetchone()
    if not active_exam:
        print("No hay ningún examen activo en este momento. Creando uno de prueba...")
        cursor.execute("""
            INSERT INTO examen (nombre, descripcion, estado, tipo_evaluacion, fecha_inicio, created_at, timer_remaining)
            VALUES ('Examen Clínico Activo', 'Examen de prueba para demostración y evaluación de ECOE/Etapa2', 'activo', 'ecoe', datetime('now'), datetime('now'), 480)
        """)
        conn.commit()
        cursor.execute("SELECT id, nombre, tipo_evaluacion FROM examen WHERE estado='activo' ORDER BY id DESC")
        active_exam = cursor.fetchone()
        
    examen_id, examen_nombre, tipo_eval = active_exam
    print(f"Examen Activo Detectado: ID={examen_id}, Nombre='{examen_nombre}', Tipo='{tipo_eval}'")

    # 2. Agregar Grupo de Alumnos (Grupo 3)
    # Lista de estudiantes para registrar en 'alumno'
    alumnos_demo = [
        (1001, 'Dra. Camila Ortega Reyes', '109520', 3),
        (1002, 'Dr. Mateo San Martín Flores', '112450', 3),
        (1003, 'Dra. Valentina Beltrán Castro', '104870', 3),
        (1004, 'Dr. Sebastián Arancibia Peña', '110320', 3),
        (1005, 'Dra. Sofía Latorre Rojas', '108540', 3),
        (1006, 'Dr. Diego Valenzuela Muñoz', '111680', 3)
    ]
    
    print("\nRegistrando alumnos de Grupo 3...")
    for alu_id, nombre, cmp, grupo in alumnos_demo:
        # Insertar o reemplazar alumno
        cursor.execute("""
            INSERT OR REPLACE INTO alumno (id, nombre, cmp, grupo)
            VALUES (?, ?, ?, ?)
        """, (alu_id, nombre, cmp, grupo))
        
        # Vincular a examen_alumno para el examen activo
        # estado: 'pendiente' o 'evaluado_parcial' para simular avance
        estado = 'pendiente'
        if alu_id in [1001, 1002, 1003]:
            estado = 'evaluado_parcial'
            
        cursor.execute("""
            INSERT OR REPLACE INTO examen_alumno (examen_id, alumno_id, estado, fecha_inscripcion)
            VALUES (?, ?, ?, datetime('now'))
        """, (examen_id, alu_id, estado))
        
    # 3. Crear evaluaciones de ejemplo con comentarios detallados (PC Maestra popovers)
    print("\nInsertando evaluaciones con comentarios clínicos detallados...")
    
    # Limpiar evaluaciones previas de estos alumnos para esta demo
    cursor.execute("""
        DELETE FROM evaluacion 
        WHERE examen_id = ? AND alumno_id IN (1001, 1002, 1003, 1004, 1005, 1006)
    """, (examen_id,))
    
    # Comentarios realistas de evaluadores en español
    evaluaciones_demo = [
        # Mateo San Martín (1002)
        (examen_id, 1002, 'e1', 18.5, 
         "El participante demostró un abordaje sumamente estructurado y empático. Realizó una técnica impecable de auscultación pulmonar ubicando los crepitantes y soplo tubárico en base derecha. Omitió evaluar los antecedentes de viajes, pero lo corrigió. En el lavado de manos quirúrgico omitió brevemente el tercer tiempo, pero se adaptó al instante. Explicó con mucha claridad y tacto las medidas y signos de alarma de Neumonía a los familiares."),
        
        (examen_id, 1002, 'e2', 17.0, 
         "Excelente manejo de crisis hipertensiva leve en paciente diabética. Calculó adecuadamente la dosis de Metformina y planteó las metas de hemoglobina glicosilada (HbA1c) con claridad. Gran empatía al comunicar el diagnóstico."),
         
        # Camila Ortega (1001)
        (examen_id, 1001, 'e1', 15.0, 
         "Buen desempeño general. Realizó una anamnesis detallada y fluida, aunque tuvo ligeras dificultades para fundamentar la dosificación exacta de Amoxicilina/Ácido Clavulánico. Ante la interrogación del jurado logró reestructurar el esquema terapéutico. Mostró un trato muy afable y profesional hacia el paciente simulado."),
         
        (examen_id, 1001, 'e2', 19.5, 
         "Desempeño sobresaliente en la estación metabólica. Elaboró la receta médica de forma impecable y sumamente legible (especificando posología exacta de Metformina y Losartán). Explicó con absoluta pedagogía y paciencia los signos de alarma de hipoglucemia al paciente simulado."),
         
        # Valentina Beltrán (1003)
        (examen_id, 1003, 'e1', 12.5, 
         "Omitió realizar el lavado de manos higiénico al ingresar al box. En el examen físico, confundió los hallazgos auscultatorios de condensación pulmonar con sibilancias difusas. Logró reencauzar la sospecha diagnóstica y formular el plan de hidratación adecuado tras la retroalimentación directa del docente evaluador.")
    ]
    
    for ex_id, alu_id, est_id, pts, coms in evaluaciones_demo:
        cursor.execute("""
            INSERT INTO evaluacion (examen_id, alumno_id, estacion_id, puntaje_total, comentarios, fecha_evaluacion)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (ex_id, alu_id, est_id, pts, coms))

    # 4. Crear Contenidos Clínicos para el Modo Evaluado (Estación 1 y Estación 2)
    print("\nCargando contenidos clínicos del Modo Evaluado...")
    
    # Limpiar contenidos previos de 'e1' y 'e2'
    cursor.execute("DELETE FROM estacion_contenido_evaluado WHERE estacion_id IN ('e1', 'e2')")
    
    contenidos_evaluado = []
    
    # ==================== ESTACIÓN 1: NEUMONÍA (ETAPA 2 - 60 MIN) ====================
    contenidos_evaluado.append((
        'e1', 'etapa2', 'caso_clinico', 'Caso Clínico: Neumonía Adquirida en la Comunidad',
        """<p><strong>Paciente:</strong> Don Aurelio Méndez, 58 años de edad.</p>
<p><strong>Motivo de Consulta:</strong> Disnea progresiva, fiebre alta y tos productiva.</p>
<p><strong>Enfermedad Actual:</strong> Paciente refiere que hace 4 días inició con malestar general, escalofríos y alza térmica no cuantificada. Posteriormente se añade tos con expectoración de aspecto herrumbroso (mucopurulenta) y sensación de falta de aire (disnea) que progresa de medianos a pequeños esfuerzos. Niega dolor torácico pleurítico y niega viajes recientes.</p>
<p><strong>Antecedentes:</strong> Hipertensión arterial en tratamiento irregular con Enalapril 20mg/día. Ex-fumador (hace 5 años, índice tabáquico de 10 paquetes/año). Alergias negadas.</p>""",
        1
    ))
    
    contenidos_evaluado.append((
        'e1', 'etapa2', 'examen_fisico', 'Examen Físico Funcional y Signos Vitales',
        """<div class="row">
  <div class="col-md-6 mb-3">
    <div class="card border shadow-xs">
      <div class="card-header bg-dark text-white fw-bold py-2"><i class="bi bi-heart-pulse-fill text-danger"></i> Signos Vitales Registrados</div>
      <ul class="list-group list-group-flush small">
        <li class="list-group-item d-flex justify-content-between"><span>Presión Arterial (PA)</span><strong>115/70 mmHg</strong></li>
        <li class="list-group-item d-flex justify-content-between"><span>Frecuencia Cardíaca (FC)</span><strong>98 lpm (Rítmico)</strong></li>
        <li class="list-group-item d-flex justify-content-between"><span>Frecuencia Respiratoria (FR)</span><strong>24 rpm (Taquipnea)</strong></li>
        <li class="list-group-item d-flex justify-content-between"><span>Temperatura Axilar (T°)</span><strong>38.9 °C (Alza térmica)</strong></li>
        <li class="list-group-item d-flex justify-content-between"><span>Saturación de Oxígeno (SatO2)</span><strong class="text-danger">92% (Aire Ambiental)</strong></li>
      </ul>
    </div>
  </div>
  <div class="col-md-6">
    <p><strong>Apreciación General:</strong> Paciente lúcido, orientado en tiempo, espacio y persona (LOTEP), en regular estado general (REG), regular estado de hidratación (REH), taquipneico, colabora activamente con el examen.</p>
    <p><strong>Aparato Respiratorio:</strong> Tórax simétrico, expansión respiratoria disminuida en base pulmonar derecha. Frémito vocal (vibraciones vocales) marcadamente aumentado en base derecha. Auscultación: <strong>Murmullo vesicular abolido/disminuido con soplo tubárico y estertores crepitantes abundantes localizados en base pulmonar derecha</strong>. No se auscultan sibilantes ni estridor laríngeo.</p>
  </div>
</div>""",
        2
    ))
    
    contenidos_evaluado.append((
        'e1', 'etapa2', 'examenes_auxiliares', 'Resultados de Laboratorio y Radiología de Tórax',
        """<p>Se solicitaron exámenes basales y de control inmediato. A continuación se detallan los resultados:</p>
<div class="row mt-3">
  <div class="col-lg-6 mb-4">
    <div class="p-3 bg-white border rounded shadow-xs h-100">
      <h6 class="fw-bold text-primary mb-2"><i class="bi bi-file-earmark-medical-fill"></i> Reporte de Laboratorio (Hemograma y PCR)</h6>
      <p class="text-muted small">Muestra leucocitosis moderada con desviación a la izquierda (neutrofilia) y elevación marcada de reactantes de fase aguda (PCR).</p>
      <img src="/static/ejemplos/analisis_sangre.png" alt="Hemograma Completo" class="img-fluid rounded border shadow-sm my-2 d-block mx-auto" style="max-height: 250px;">
    </div>
  </div>
  <div class="col-lg-6 mb-4">
    <div class="p-3 bg-white border rounded shadow-xs h-100">
      <h6 class="fw-bold text-primary mb-2"><i class="bi bi-lungs-fill text-info"></i> Radiografía de Tórax (Incidencia AP)</h6>
      <p class="text-muted small">Evidencia un área radiopaca homogénea de consolidación alveolar circunscrita al lóbulo inferior derecho con broncograma aéreo.</p>
      <img src="/static/ejemplos/rx_torax.png" alt="Radiografía de Tórax" class="img-fluid rounded border shadow-sm my-2 d-block mx-auto" style="max-height: 250px;">
    </div>
  </div>
</div>""",
        3
    ))
    
    contenidos_evaluado.append((
        'e1', 'etapa2', 'tratamiento', 'Plan Terapéutico y Receta Médica Sugerida',
        """<p><strong>Medidas de Soporte:</strong> Reposo relativo, hidratación oral abundante para facilitar la fluidificación de secreciones. Soporte oxigenatorio intermitente por cánula binasal a 2 litros/minuto en caso de que SatO2 disminuya a &lt; 92% de forma persistente.</p>
<p><strong>Tratamiento Antibiótico:</strong> Evaluado bajo escala CURB-65 (Puntaje: 1 punto - Confusión (-), Urea (-), FR (+) (24 rpm), PA (-), Edad <65 (-)). Se indica manejo ambulatorio vigilado con terapia vía oral por 7 días:</p>

<div class="bg-light p-3 border rounded shadow-xs my-3">
  <p class="mb-2"><strong>1. Amoxicilina 875mg + Ácido Clavulánico 125mg:</strong> Tomar 1 tableta vía oral cada 12 horas por 7 días.</p>
  <p class="mb-0"><strong>2. Paracetamol 500mg:</strong> Tomar 1 tableta vía oral cada 8 horas únicamente en caso de fiebre (T° &gt; 38.0°C) o dolor pleurítico.</p>
</div>

<div class="text-center mt-3">
  <span class="small text-secondary fw-semibold d-block mb-2">Vista del Modelo de Receta Oficial para el Paciente:</span>
  <img src="/static/ejemplos/receta_medica.png" alt="Modelo de Receta Médica" class="img-fluid rounded border shadow-sm" style="max-height: 320px; display: block; margin: 0 auto;">
</div>""",
        4
    ))
    
    contenidos_evaluado.append((
        'e1', 'etapa2', 'indicaciones', 'Criterios de Alta e Indicaciones al Paciente',
        """<h6 class="fw-bold text-danger mb-2"><i class="bi bi-exclamation-triangle-fill"></i> Criterios de Retorno Inmediato a Emergencia:</h6>
<p>Debe instruirse formalmente al paciente y a su familia acudir de urgencia si se presenta:</p>
<ul class="small mb-3">
  <li>Dificultad marcada para respirar o aumento de la taquipnea (&gt; 30 rpm).</li>
  <li>Coloración azulada de labios o lecho ungueal (cianosis distal).</li>
  <li>Alteración del sensorio (desorientación, confusión, tendencia al sueño).</li>
  <li>Intolerancia absoluta a la vía oral (vómitos incoercibles).</li>
  <li>Persistencia de picos febriles elevados pasadas las 48-72 horas de tratamiento.</li>
</ul>

<h6 class="fw-bold text-success mt-3 mb-2"><i class="bi bi-calendar-check-fill"></i> Seguimiento Clínico y Control:</h6>
<p>Cita presencial en consulta externa en 48-72 horas para documentar remisión de síntomas de la neumonía. Radiografía de tórax de control evolutivo en 4 a 6 semanas para confirmar resolución de la opacidad basal.</p>""",
        5
    ))
    
    # ==================== ESTACIÓN 1: NEUMONÍA (ECOE - 8 MIN) ====================
    # El ECOE es más breve, rápido, sintético.
    contenidos_evaluado.append((
        'e1', 'ecoe', 'caso_clinico', 'Caso Clínico Rápido (ECOE): Neumonía Agquirida en Comunidad',
        """<p><strong>Ficha de Datos:</strong> Varón de 58 años con tos con expectoración herrumbrosa, fiebre de 39°C y disnea progresiva de 4 días de evolución.</p>
<p><strong>Antecedentes:</strong> Hipertenso controlado. Ex-fumador.</p>
<p><strong>Tarea del Participante:</strong> Realizar anamnesis dirigida, auscultación pulmonar en 2 minutos, dar diagnóstico presuntivo y plantear el esquema farmacológico adecuado de forma concisa.</p>""",
        1
    ))
    
    contenidos_evaluado.append((
        'e1', 'ecoe', 'examen_fisico', 'Auscultación y Signos Vitales (ECOE)',
        """<p><strong>Signos Vitales:</strong> PA: 115/70, FC: 98 lpm, FR: 24 rpm, Temp: 38.9°C, SatO2: 92% (Aire Ambiental).</p>
<p><strong>Aparato Respiratorio:</strong> Hallazgo cardinal: <strong>crepitantes abundantes en base pulmonar derecha con soplo tubárico y abolición del murmullo vesicular</strong>.</p>""",
        2
    ))
    
    contenidos_evaluado.append((
        'e1', 'ecoe', 'examenes_auxiliares', 'Resultados Auxiliares (ECOE)',
        """<p><strong>Hemograma:</strong> 15,200 leucocitos/uL (88% segmentados), PCR: 58 mg/L.</p>
<p><strong>Rx Tórax:</strong> Consolidación alveolar lobar inferior derecha compatible con Neumonía bacteriana.</p>
<div class="text-center my-2">
  <img src="/static/ejemplos/rx_torax.png" alt="Radiografía de Tórax" class="img-fluid rounded border shadow-sm" style="max-height: 180px;">
</div>""",
        3
    ))
    
    contenidos_evaluado.append((
        'e1', 'ecoe', 'tratamiento', 'Tratamiento Empírico Ambulatorio (ECOE)',
        """<p><strong>Esquema Antibiótico de Elección (CURB-65: 1 punto - Ambulatorio):</strong></p>
<ul>
  <li>Amoxicilina 875mg + Ácido Clavulánico 125mg VO cada 12 horas por 7 días.</li>
  <li>Paracetamol 500mg VO cada 8 horas condicionado a fiebre.</li>
</ul>
<div class="text-center my-2">
  <img src="/static/ejemplos/receta_medica.png" alt="Receta" class="img-fluid rounded border shadow-sm" style="max-height: 180px;">
</div>""",
        4
    ))
    
    contenidos_evaluado.append((
        'e1', 'ecoe', 'indicaciones', 'Criterios de Alarma Críticos (ECOE)',
        """<p>Instruir al paciente sobre los 3 signos de retorno inmediato: disnea extrema (falta de aire grave), alteración del estado de conciencia o intolerancia oral. Control clínico obligatorio en 48-72 horas.</p>""",
        5
    ))

    # ==================== ESTACIÓN 2: DIABETES Y CRISIS HIPERTENSIVA (ETAPA 2) ====================
    contenidos_evaluado.append((
        'e2', 'etapa2', 'caso_clinico', 'Caso Clínico: Diabetes Mellitus Tipo 2 y Crisis Hipertensiva Leve',
        """<p><strong>Paciente:</strong> Doña Rosa María Delgado, 62 años de edad.</p>
<p><strong>Motivo de Consulta:</strong> Poliuria, polidipsia marcada, pérdida de peso involuntaria y cefalea occipital ocasional.</p>
<p><strong>Enfermedad Actual:</strong> Paciente acude refiriendo sed excesiva (polidipsia) y aumento notable de la frecuencia urinaria (poliuria) de 2 meses de evolución. En las últimas 3 semanas ha notado pérdida de peso de aproximadamente 4 kg sin causa aparente, fatiga constante y cefalea occipital leve recurrente.</p>
<p><strong>Antecedentes:</strong> Madre con Diabetes Mellitus. Obesidad Grado I diagnosticada hace 1 año sin seguimiento dietético.</p>""",
        1
    ))
    
    contenidos_evaluado.append((
        'e2', 'etapa2', 'examen_fisico', 'Examen Físico y Medidas Antropométricas',
        """<div class="row">
  <div class="col-md-6 mb-3">
    <div class="card border shadow-xs">
      <div class="card-header bg-dark text-white fw-bold py-2"><i class="bi bi-activity"></i> Signos Vitales y Antropometría</div>
      <ul class="list-group list-group-flush small">
        <li class="list-group-item d-flex justify-content-between"><span>Presión Arterial (PA)</span><strong class="text-danger">150/95 mmHg (Elevada)</strong></li>
        <li class="list-group-item d-flex justify-content-between"><span>Frecuencia Cardíaca (FC)</span><strong>82 lpm (Rítmico)</strong></li>
        <li class="list-group-item d-flex justify-content-between"><span>Temperatura Axilar (T°)</span><strong>36.6 °C (Afebril)</strong></li>
        <li class="list-group-item d-flex justify-content-between"><span>Índice de Masa Corporal (IMC)</span><strong>31.2 kg/m² (Obesidad Grado I)</strong></li>
      </ul>
    </div>
  </div>
  <div class="col-md-6">
    <p><strong>Apreciación General:</strong> Paciente lúcida, orientada, obesa, colaboradora con el examen físico, afebril.</p>
    <p><strong>Examen Cardiovascular:</strong> Ruidos cardíacos rítmicos, normofonéticos, sin soplos. Pulsos periféricos presentes y simétricos, aunque ligeramente disminuidos en miembros inferiores.</p>
    <p><strong>Piel y Faneras:</strong> Presencia de <strong>Acantosis Nigricans moderada en región posterior del cuello y axilas</strong>, compatible con resistencia periférica a la insulina severa.</p>
  </div>
</div>""",
        2
    ))
    
    contenidos_evaluado.append((
        'e2', 'etapa2', 'examenes_auxiliares', 'Exámenes de Laboratorio Metabólico',
        """<p>Se detallan los resultados del perfil metabólico y renal solicitados:</p>
<ul class="small mb-3">
  <li><strong>Glucosa en Ayunas:</strong> <strong class="text-danger">210 mg/dL</strong> (Valor de referencia: 70-100 mg/dL).</li>
  <li><strong>Hemoglobina Glicosilada (HbA1c):</strong> <strong class="text-danger">8.4%</strong> (Valor objetivo en adulto mayor saludable: &lt; 7.0% - 7.5%).</li>
  <li><strong>Creatinina Séptica:</strong> <strong>0.9 mg/dL</strong> (Función renal conservada).</li>
  <li><strong>Colesterol Total:</strong> <strong class="text-danger">245 mg/dL</strong> (Dislipidemia mixta).</li>
  <li><strong>Triglicéridos:</strong> <strong class="text-danger">210 mg/dL</strong> (Elevados).</li>
</ul>
<div class="p-3 bg-white border rounded shadow-xs text-center">
  <h6 class="fw-bold text-primary mb-2"><i class="bi bi-file-earmark-medical-fill"></i> Reporte Analítico Metabólico Completo</h6>
  <img src="/static/ejemplos/analisis_sangre.png" alt="Analisis de Sangre" class="img-fluid rounded border shadow-sm my-2 d-block mx-auto" style="max-height: 250px;">
</div>""",
        3
    ))
    
    contenidos_evaluado.append((
        'e2', 'etapa2', 'tratamiento', 'Tratamiento Inicial de Diabetes y Control de Presión Arterial',
        """<p><strong>Plan No Farmacológico:</strong> Modificación estricta del estilo de vida (Menejo dietético hipocalórico, reducción drástica de carbohidratos simples y grasas saturadas, actividad física aeróbica 150 minutos semanales divididos en 5 días).</p>
<p><strong>Tratamiento Farmacológico Inicial:</strong> Debido a HbA1c de 8.4% se indica terapia oral combinada inicial para Diabetes y control del riesgo cardiovascular / crisis hipertensiva:</p>

<div class="bg-light p-3 border rounded shadow-xs my-3">
  <p class="mb-2"><strong>1. Metformina 850mg:</strong> Tomar 1 tableta vía oral con el almuerzo y otra tableta con la cena (cada 12 horas) por tiempo indefinido.</p>
  <p class="mb-0"><strong>2. Losartán 50mg:</strong> Tomar 1 tableta vía oral cada 24 horas por las mañanas de forma indefinida.</p>
</div>

<div class="text-center mt-3">
  <span class="small text-secondary fw-semibold d-block mb-2">Vista del Modelo de Receta para Doña Rosa María:</span>
  <img src="/static/ejemplos/receta_medica.png" alt="Modelo de Receta Médica" class="img-fluid rounded border shadow-sm" style="max-height: 320px; display: block; margin: 0 auto;">
</div>""",
        4
    ))
    
    contenidos_evaluado.append((
        'e2', 'etapa2', 'indicaciones', 'Monitoreo, Metas Clínicas y Signos de Alerta',
        """<h6 class="fw-bold text-warning mb-2"><i class="bi bi-display"></i> Automonitoreo Capilar en Domicilio:</h6>
<p>Glucemia capilar en ayunas (meta: 80-130 mg/dL) y glucemia postprandial 2 horas después de las comidas (meta: &lt; 180 mg/dL).</p>

<h6 class="fw-bold text-danger mt-3 mb-2"><i class="bi bi-shield-fill-exclamation"></i> Signos de Alerta Inmediatos (Hipoglucemia):</h6>
<p>Educar a la paciente si presenta sudoración fría, temblor, mareos, palpitaciones o confusión mental severa. En estos casos, consumir de inmediato 15 gramos de carbohidratos rápidos (ej: medio vaso de jugo azucarado) y reevaluar glucemia en 15 minutos (Regla de los 15).</p>""",
        5
    ))

    # ==================== ESTACIÓN 2: DIABETES (ECOE - 8 MIN) ====================
    contenidos_evaluado.append((
        'e2', 'ecoe', 'caso_clinico', 'Caso Clínico Rápido (ECOE): Diabetes Mellitus Tipo 2',
        """<p><strong>Ficha:</strong> Paciente mujer de 62 años con poliuria, polidipsia, IMC: 31.2 y PA: 150/95 mmHg.</p>
<p><strong>Laboratorio:</strong> Glucosa: 210 mg/dL, HbA1c: 8.4%.</p>
<p><strong>Tarea:</strong> Explicar de forma asertiva el diagnóstico de Diabetes Mellitus, redactar el plan terapéutico inicial con Metformina y Losartán en la receta, y educar sobre hipoglucemia en 5 minutos.</p>""",
        1
    ))
    
    contenidos_evaluado.append((
        'e2', 'ecoe', 'examen_fisico', 'Examen Físico Dirigido (ECOE)',
        """<p>PA: 150/95 mmHg, IMC: 31.2 (Obesidad Grado I), presencia de Acantosis Nigricans en cuello.</p>""",
        2
    ))
    
    contenidos_evaluado.append((
        'e2', 'ecoe', 'examenes_auxiliares', 'Perfil Metabólico Rápido (ECOE)',
        """<p>Glucosa ayunas: 210 mg/dL, HbA1c: 8.4%, perfil lipídico alterado. Se muestra reporte en pantalla:</p>
<div class="text-center my-2">
  <img src="/static/ejemplos/analisis_sangre.png" alt="Analisis Sangre" class="img-fluid rounded border shadow-sm" style="max-height: 180px;">
</div>""",
        3
    ))
    
    contenidos_evaluado.append((
        'e2', 'ecoe', 'tratamiento', 'Tratamiento Inicial Combinado (ECOE)',
        """<p>Indicación terapéutica inmediata:</p>
<ul>
  <li>Metformina 850mg VO cada 12 horas junto con alimentos.</li>
  <li>Losartán 50mg VO cada 24 horas.</li>
</ul>
<div class="text-center my-2">
  <img src="/static/ejemplos/receta_medica.png" alt="Receta" class="img-fluid rounded border shadow-sm" style="max-height: 180px;">
</div>""",
        4
    ))
    
    contenidos_evaluado.append((
        'e2', 'ecoe', 'indicaciones', 'Criterios Críticos de Consejería (ECOE)',
        """<p>Educar en la Regla de los 15 ante síntomas de hipoglucemia (sudoración, temblor, mareos). Citar a control de PA en 7 días y control de HbA1c en 3 meses.</p>""",
        5
    ))

    print(f"Insertando {len(contenidos_evaluado)} registros de contenidos clínicos...")
    for est_id, etapa, seccion, titulo, contenido, orden in contenidos_evaluado:
        cursor.execute("""
            INSERT INTO estacion_contenido_evaluado (estacion_id, etapa, seccion, titulo, contenido, orden, visible, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 1, datetime('now'))
        """, (est_id, etapa, seccion, titulo, contenido, orden))
        
    conn.commit()
    print("\n¡Carga de datos de ejemplo realizada de forma EXITOSA!")
    
    # 5. Imprimir resumen
    cursor.execute("SELECT COUNT(*) FROM alumno WHERE grupo=3")
    print(f"Alumnos de Grupo 3 en DB: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM examen_alumno WHERE examen_id=?", (examen_id,))
    print(f"Alumnos vinculados al Examen {examen_id} en DB: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM evaluacion WHERE examen_id=?", (examen_id,))
    print(f"Evaluaciones registradas en Examen {examen_id} en DB: {cursor.fetchone()[0]}")
    cursor.execute("SELECT COUNT(*) FROM estacion_contenido_evaluado")
    print(f"Contenidos de evaluado totales en DB: {cursor.fetchone()[0]}")
    
    conn.close()

if __name__ == '__main__':
    populate()
