import React from 'react'
import './About.css'
import about_img from '../../assets/about.png'
import play_icon from '../../assets/play-icon.png'

const About = ({setPlayState}) => {
  return (
    <div className='about'>
      <div className="about-left">
        <img src={about_img} alt="" className='about-img'/>
        <img src={play_icon} alt="" className='play-icon' onClick={()=>{setPlayState(true)}}/>
      </div>
      <div className="about-right">
        <h3>SOBRE UNIVERSIDAD DEL NORTE</h3>
        <h2>Alimentando a las líderes del mañana hoy</h2>
        <p>Embárcate en un viaje educativo transformador con los programas educativos integrales de nuestra universidad. Nuestro currículo está diseñado para dotar a los estudiantes de los conocimientos, las habilidades y las experiencias necesarias para sobresalir en el dinámico campo de la educación.</p>
        <p>Con un enfoque en la innovación, el aprendizaje práctico y la tutoría personalizada, con nuestro grupo CREE, nuestros programas preparan a los aspirantes a educadores para generar un impacto significativo en las aulas, las escuelas y las comunidades.</p>
        <p>Ya sea que aspire a convertirse en maestro, administrador, consejero o líder educativo, nuestra diversa gama de programas ofrece el camino perfecto para lograr sus objetivos y desbloquear todo su potencial para dar forma al futuro de la educación.</p>
      </div>
    </div>
  )
}

export default About
