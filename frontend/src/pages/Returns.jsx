import React from 'react';
import PageTransition from '../components/PageTransition';
import './SupportPages.css';

const Returns = () => {
  return (
    <PageTransition>
      <div className="support-page container">
        <div className="support-header">
          <h1>Política de Devoluciones</h1>
          <p>Nuestra prioridad es la calidad y tu satisfacción. Conoce nuestras políticas de cambio y devolución.</p>
        </div>

        <div className="support-content legal-text glass-panel" style={{ padding: '40px' }}>
          <h2>1. Garantía de Calidad KR Cases</h2>
          <p>
            Todos nuestros productos pasan por un riguroso control de calidad antes de ser enviados. Sin embargo, si recibes un producto con defectos de fábrica o daños ocasionados durante el envío, tienes derecho a solicitar un cambio o reembolso dentro de los primeros <strong>30 días naturales</strong> desde la fecha de recepción.
          </p>

          <h2>2. Condiciones para Cambios</h2>
          <p>Para que un cambio o devolución sea procesado, el producto debe cumplir con lo siguiente:</p>
          <ul>
            <li>El artículo debe estar sin uso y en las mismas condiciones en que lo recibiste.</li>
            <li>Debe conservar su empaque original impecable.</li>
            <li>Es necesario presentar el comprobante de compra o número de pedido.</li>
          </ul>

          <h2>3. Productos no elegibles</h2>
          <p>No se aceptarán devoluciones ni cambios en los siguientes casos:</p>
          <ul>
            <li>Fundas que muestren signos evidentes de uso, rayaduras o caídas posteriores a la entrega.</li>
            <li>Errores por parte del cliente al momento de seleccionar el modelo de su dispositivo en la tienda web.</li>
            <li>Fundas personalizadas o de ediciones limitadas a pedido.</li>
          </ul>

          <h2>4. ¿Cómo solicitar un cambio?</h2>
          <p>
            Para iniciar el proceso de devolución, por favor contáctanos vía WhatsApp al <strong>+595 991 597 314</strong> o envíanos un correo a <strong>info@krcases.com</strong> con fotografías claras del producto y tu número de orden. Nuestro equipo evaluará tu caso y te guiará con los siguientes pasos en un plazo máximo de 48 horas.
          </p>

          <h2>5. Costos de Envío</h2>
          <p>
            Si la devolución es por un error nuestro o un defecto de fábrica, nosotros cubrimos el costo de envío. Si el cambio se solicita por otro motivo aprobado (como cambio de color), el cliente deberá hacerse cargo de los costos de envío asociados.
          </p>
        </div>
      </div>
    </PageTransition>
  );
};

export default Returns;
