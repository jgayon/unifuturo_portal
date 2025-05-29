import React from 'react'
import './Contact.css'
import msg_icon from '../../assets/msg-icon.png'
import mail_icon from '../../assets/mail-icon.png'
import phone_icon from '../../assets/phone-icon.png'
import location_icon from '../../assets/location-icon.png'
import white_arrow from '../../assets/white-arrow.png'

const Contact = () => {

    const [result, setResult] = React.useState("");

    const onSubmit = async (event) => {
      event.preventDefault();
      setResult("Enviando....");
      const formData = new FormData(event.target);

      // ------Enter your web3forms access key below-------
      
      formData.append("access_key", "9fedb577-b432-4bc5-bb10-6fdda8341826");
  
      const res = await fetch("https://api.web3forms.com/submit", {
        method: "POST",
        body: formData
      }).then((res) => res.json());
  
      if (res.success) {
        console.log("Success", res);
        // setResult(res.message);
        setResult("¡Tu mensaje fue enviado exitosamente!");
        event.target.reset();
      } else {
        console.log("Error", res);
        // setResult(res.message);
        setResult("Hubo un error al enviar tu mensaje. Intenta nuevamente.");
      }
    };


  return (
    <div className='contact'>
      <div className="contact-col">
        <h3>Envíanos un mensaje<img src={msg_icon} alt="" /></h3>
        <p>No dude en contactarnos a través del formulario de contacto o consultar nuestra información de contacto a continuación. Sus comentarios, preguntas y sugerencias son importantes para nosotros, ya que nos esforzamos por brindar un servicio excepcional a nuestra comunidad universitaria.</p>
        <ul>
            <li><img src={mail_icon} alt="" />Contact@Unifuturo.co</li>
            <li><img src={phone_icon} alt="" />+57 320-456-9512</li>
            <li><img src={location_icon} alt="" />Km 5 Barranquilla, Puerto Colombia<br/> AT 150001, Colombia</li>
        </ul>
      </div>
      <div className="contact-col">
        <form onSubmit={onSubmit}>
            <label>Nombre</label>
            <input type="text" name='name' placeholder='Escribe tu nombre' required/>
            <label>Número de teléfono</label>
            <input type="tel" name='phone' placeholder='Escribe tu número de teléfono' required/>
            <label>Escribe tus mensajes aquí</label>
            <textarea name="message" rows="6" placeholder='Escribe tu mensajes' required></textarea>
            <button type='submit' className='btn dark-btn'>Enviar ahora<img src={white_arrow} alt="" /></button>
        </form>
        <span>{result}</span>
      </div>
    </div>
  )
}

export default Contact
