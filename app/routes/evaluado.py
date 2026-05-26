from flask import Blueprint, render_template, redirect, flash, url_for, abort
from app.models.models import Examen, Estacion, EstacionContenidoEvaluado
from extensions import db

evaluado_bp = Blueprint('evaluado', __name__)

def get_active_exam():
    return Examen.query.filter_by(estado='activo').order_by(Examen.id.desc()).first()

@evaluado_bp.route('/')
def index():
    examen_activo = get_active_exam()
    return render_template('evaluado_index.html', examen_activo=examen_activo)

@evaluado_bp.route('/<etapa>')
def estaciones(etapa):
    if etapa not in ['etapa2', 'ecoe']:
        abort(404)
        
    examen_activo = get_active_exam()
    if not examen_activo:
        flash('No hay examen activo en este momento.', 'warning')
        
    estaciones_list = Estacion.query.filter_by(activa=True).order_by(Estacion.orden).all()
    return render_template(
        'evaluado_estaciones.html',
        etapa=etapa,
        estaciones=estaciones_list,
        examen_activo=examen_activo
    )

@evaluado_bp.route('/<etapa>/<estacion_id>')
def estacion_contenido(etapa, estacion_id):
    if etapa not in ['etapa2', 'ecoe']:
        abort(404)
        
    estacion = Estacion.query.get_or_404(estacion_id)
    if not estacion.esta_activa:
        flash('Esta estación está inactiva y no está disponible.', 'warning')
        return redirect(url_for('evaluado.estaciones', etapa=etapa))
        
    examen_activo = get_active_exam()
    
    # Query all visible content for this station, stage, sorted by order
    contenidos = EstacionContenidoEvaluado.query.filter_by(
        estacion_id=estacion_id,
        etapa=etapa,
        visible=True
    ).order_by(EstacionContenidoEvaluado.orden).all()
    
    # Group content by sections
    # sections: 'caso_clinico', 'examen_fisico', 'examenes_auxiliares', 'tratamiento', 'indicaciones'
    contenidos_por_seccion = {
        'caso_clinico': [],
        'examen_fisico': [],
        'examenes_auxiliares': [],
        'tratamiento': [],
        'indicaciones': []
    }
    
    for c in contenidos:
        if c.seccion in contenidos_por_seccion:
            contenidos_por_seccion[c.seccion].append(c)
        else:
            if c.seccion not in contenidos_por_seccion:
                contenidos_por_seccion[c.seccion] = []
            contenidos_por_seccion[c.seccion].append(c)
            
    return render_template(
        'evaluado_estacion.html',
        etapa=etapa,
        estacion=estacion,
        contenidos_por_seccion=contenidos_por_seccion,
        examen_activo=examen_activo
    )
