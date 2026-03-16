import { Button, Card, Form, Input } from 'antd';
import React,{useCallback, useContext} from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from '../../context/AuthContext';
import logo from '../images/logo-no-background.png';

const baseURL = process.env.REACT_APP_BASE_URL
export default function  ForgotPassword(){
    let navigate = useNavigate()
    const {messageApi} = useContext(AuthContext)


    const SendMail = useCallback(async(values) =>{
        let response = await fetch(`${baseURL}/account/forgot_password/send_mail/`,{
            method:"POST",
            headers:{
                'Content-Type':"application/json"
            },
            body:JSON.stringify(values)
        })
        let data = await response.json()

        if (data.status === 1){
            messageApi.open({type: 'success',content: data.message})
            navigate("/login")
        }
        else{
            messageApi.open({type: 'error',content: data.message})
        }
    }, [messageApi, navigate])

    return(
        <>
            <div className="main_div">
                <div className="login_div">
                    <div style={{margin: '22px'}}>
                        <img src={logo} alt="logo-no-background.png" style={{width:"300px"}}></img>
                    </div>
                    <Card title="Reset your password" className='login_card' bordered={true}>
                        <div style={{ marginBottom: '16px' }}>
                            Enter your register Email address and we will send you instructions to reset your password.
                        </div>
                        <Form name="basic" labelCol={{flex: '110px'}} labelAlign="left" wrapperCol={{span: 16,}}style={{maxWidth: 600}}
                            initialValues={{remember: true,}} onFinish={SendMail} autoComplete="off">
                            <Form.Item label="Email" name="email" rules={[{required: true, message: 'Please enter your email!',},]}>
                                <Input />
                            </Form.Item>

                            <Form.Item style={{ margin: '0px 107px'}}>
                                <Button type="primary" htmlType="submit" style={{ width: "300px"}}>Send Mail</Button>
                            </Form.Item>

                        </Form>

                    </Card>
                </div>
            </div>
        </>
    )
}