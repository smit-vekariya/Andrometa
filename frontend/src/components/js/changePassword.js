import { Button, Card, Form, Input } from 'antd';
import React,{useContext, useCallback} from "react";
import { useNavigate, useParams } from "react-router-dom";
import { AuthContext } from '../../context/AuthContext';
import logo from '../images/logo-no-background.png';
const baseURL = process.env.REACT_APP_BASE_URL

export default function ChangePassword(){
    let navigate = useNavigate()
    const {messageApi} = useContext(AuthContext)
    const {uid, token} = useParams()

    const RestPassword = useCallback(async(values) =>{
        if(values.password !== values.confirm_password){
            messageApi.open({type: 'error',content: "password does not match!"})
            return 0
        }

        values.uid= uid
        values.token = token
        let response = await fetch(`${baseURL}/account/forgot_password/change_password/`,{
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
    }, [messageApi, navigate, uid, token])


    return(
        <>
            <div className="main_div">
                <div className="login_div">
                    <div style={{margin: '22px'}}>
                        <img src={logo} alt="logo-no-background.png" style={{width:"300px"}}></img>
                    </div>
                    <Card title="Change your password" className='login_card' bordered={true}>
                        <div style={{ marginBottom: '16px' }}>
                            Enter a new password below to change your password.<br />
                        </div>

                        <Form name="basic" labelCol={{flex: '133px'}} labelAlign="left" wrapperCol={{span: 16,}}style={{maxWidth: 600}}
                            initialValues={{remember: true,}} onFinish={RestPassword} autoComplete="off">

                            <Form.Item label="Password" name="password" rules={[{required: true, message: 'Please enter your password!',},]}>
                                <Input.Password />
                            </Form.Item>
                            <Form.Item label="Confirm Password" name="confirm_password" rules={[{required: true, message: 'Password not matched!',},]}>
                                <Input.Password />
                            </Form.Item>

                            <Form.Item style={{ margin: '0px 72px'}}>
                                <Button type="primary" htmlType="submit" style={{ width: "300px"}}>Reset Password</Button>
                            </Form.Item>

                        </Form>

                    </Card>
                </div>
            </div>
        </>
    )
}