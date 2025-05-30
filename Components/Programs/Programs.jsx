import React from 'react'
// agg
import { useNavigate } from 'react-router-dom';
import './Programs.css'
import program_1 from '../../assets/program-1.png'
import program_2 from '../../assets/program-2.png'
import program_3 from '../../assets/program-3.png'
import program_icon_1 from '../../assets/program-icon-1.png'
import program_icon_2 from '../../assets/program-icon-2.png'
import program_icon_3 from '../../assets/program-icon-3.png'

const Programs = () => {
  // agg
  const navigate = useNavigate();

  // //agg
  // const handleGraduationClick = () => {
  //   navigate('/program-selection');
  // }
  // agg:  onClick={() => navigate('/program-selection')}
  return (
    <div className='programs'>
      <div className="program" onClick={() => navigate('/program-selection')}>
        <img src={program_1} alt="" />
        <div className="caption">
            <img src={program_icon_1} alt="" />
            <p>Pregrado</p>
        </div>
      </div>
      <div className="program">
        <img src={program_2} alt="" />
        <div className="caption">
            <img src={program_icon_2} alt="" />
            <p>Maestría</p>
        </div>
      </div>
      <div className="program">
        <img src={program_3} alt="" />
        <div className="caption">
            <img src={program_icon_3} alt="" />
            <p>Postgrado</p>
        </div>
      </div>
    </div>
  )
}

export default Programs
