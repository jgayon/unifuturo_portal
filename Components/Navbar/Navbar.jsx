import React, { useEffect, useState } from 'react'
// import css file
import './Navbar.css'
// import images
// import logo from '../../assets/logo.png'
import logo from '../../assets/unifuturo-logo.png';
import menu_icon from '../../assets/menu-icon.png'
import { Link } from 'react-scroll';


const Navbar = () => {

    const [sticky, setSticky] = useState(false);

    useEffect(()=>{
        window.addEventListener('scroll', ()=>{
            window.scrollY > 50 ? setSticky(true) : setSticky(false);
        })
    },[]);


    const [mobileMenu, setMobileMenu] = useState(false);
    const toggleMenu = ()=>{
      mobileMenu ? setMobileMenu(false) : setMobileMenu(true);
    }

  return (
    // import images and links
    <nav className={`container ${sticky? 'dark-nav' : ''}`}>
      <img src={logo} alt="" className='logo' />
      <ul className={mobileMenu?'':'hide-mobile-menu'}>
        <li><Link to='hero' smooth={true} offset={0} duration={500}>Inicio</Link></li>
        <li><Link to='program' smooth={true} offset={-260} duration={500}>Programas</Link></li>
        <li><Link to='about' smooth={true} offset={-150} duration={500}>Sobre nosotros</Link></li>
        <li><Link to='campus' smooth={true} offset={-260} duration={500}>Campus</Link></li>
        <li><Link to='testimonials' smooth={true} offset={-260} duration={500}>Testimonios</Link></li>
        <li><Link to='contact' smooth={true} offset={-260} duration={500} className='btn'>Contactanos</Link></li>
      </ul>
      <img src={menu_icon} alt="" className='menu-icon' onClick={toggleMenu}/>
    </nav>
  )
}

export default Navbar
