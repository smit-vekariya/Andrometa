import { Card, Col, Row } from 'antd';
import React, { useCallback, useContext, useEffect, useRef, useState } from "react";
import { AuthContext } from '../../context/AuthContext';
import useAxios from '../../utils/useAxios';
import user_img from "../images/user.png";


export default function CompanyDashBoard(){
    const api = useRef(useAxios())
    const [dashboard, setDashBoard] = useState({})
    const {messageApi} = useContext(AuthContext)

    const getDashBoardData = useCallback(async() =>{
        await api.current.get('/qr_admin/dashboard/')
        .then((res)=>{
            setDashBoard(res.data.data[0])
        })
        .catch((error)=>{
            messageApi.open({type: 'error',content: error.message})
        })
    },[messageApi])


    useEffect(()=>{
        getDashBoardData()
    },[getDashBoardData])

    return(
        <>
        <div className='title_tab'>
            <div className='title_tab_title'>Dashboard</div>
        </div>
        <div className='main_tab'>
            <Row>
                <Col span={8}>
                    <Card title="Total User" bordered={true}>
                        <img src={user_img} alt="user.png" style={{width:"50px", marginRight: '15px' }}></img>
                        <p><b>{dashboard.total_bond_user}</b></p>
                    </Card>
                </Col>
            </Row>
        </div>
        </>
    )
}