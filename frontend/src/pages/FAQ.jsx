import React, { useState } from 'react';
import { ChevronDown } from 'lucide-react';
import PageTransition from '../components/PageTransition';
import './SupportPages.css';

const faqs = [
  {
    q: "¿Cuánto tiempo tarda en llegar mi pedido?",
    a: "Para entregas en Asunción y Gran Asunción, el envío se realiza en 24 horas hábiles. Para el interior del país, el tiempo estimado es de 48 a 72 horas hábiles dependiendo de la agencia de encomiendas."
  },
  {
    q: "¿Cuáles son los métodos de pago aceptados?",
    a: "Actualmente aceptamos pago contra entrega en efectivo y transferencias bancarias directas. Pronto habilitaremos el pago con tarjetas de crédito."
  },
  {
    q: "¿Las fundas tienen garantía?",
    a: "Sí, todos nuestros productos de KR Cases cuentan con una garantía de 30 días contra defectos de fábrica. Queremos que estés 100% satisfecho con tu compra."
  },
  {
    q: "¿Cómo sé si la funda es compatible con mi teléfono?",
    a: "En la página de cada producto encontrarás un selector de modelo. Asegúrate de elegir exactamente el modelo de tu smartphone (por ejemplo, iPhone 15 Pro Max o Samsung S24 Ultra). Nuestras fundas están hechas a medida para cada variante."
  },
  {
    q: "¿Las fundas transparentes se ponen amarillas?",
    a: "Nuestra línea Crystal Clear utiliza policarbonato con tratamiento anti-amarilleo (Anti-Yellowing Tech) que retrasa significativamente el desgaste por rayos UV, manteniéndose transparentes por mucho más tiempo que las fundas de silicona comunes."
  }
];

const FAQ = () => {
  const [openIndex, setOpenIndex] = useState(null);

  const toggleFAQ = (index) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <PageTransition>
      <div className="support-page container">
        <div className="support-header">
          <h1>Preguntas Frecuentes</h1>
          <p>Encuentra respuestas rápidas a las dudas más comunes sobre nuestros productos, envíos y políticas.</p>
        </div>

        <div className="support-content">
          {faqs.map((faq, index) => (
            <div 
              key={index} 
              className={`faq-item ${openIndex === index ? 'active' : ''}`}
            >
              <div 
                className="faq-question" 
                onClick={() => toggleFAQ(index)}
              >
                {faq.q}
                <ChevronDown 
                  size={20} 
                  className={`faq-icon ${openIndex === index ? 'open' : ''}`} 
                />
              </div>
              <div className={`faq-answer ${openIndex === index ? 'open' : ''}`}>
                {faq.a}
              </div>
            </div>
          ))}
        </div>
      </div>
    </PageTransition>
  );
};

export default FAQ;
