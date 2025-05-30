import React from 'react'
import './Hero.css'
import dark_arrow from '../../assets/dark-arrow.png'

const Hero = () => {
  return (
    <div className='hero container'>
      <div className="hero-text">
        <h1>Garantizamos una mejor educación para un mundo mejor</h1>
        <p>Nuestro plan de estudios de vanguardia está diseñado para capacitar a los estudiantes con el conocimiento, las habilidades y las experiencias necesarias para sobresalir en el dinámico campo de la educación.</p>
        {/* <button className='btn'>Ingresar aqui<img src={dark_arrow} alt="" /></button> */}
        <a href="http://127.0.0.1:5000/" className="btn">
          Ingresar aquí <img src={dark_arrow} alt="" />
        </a>
      </div>
    </div>
  )
}

export default Hero
