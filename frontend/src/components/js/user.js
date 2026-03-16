import { Button, Form, Input, Modal, Table, Tag } from 'antd';
import React, { useCallback, useContext, useEffect, useRef, useState } from "react";
import { AuthContext } from '../../context/AuthContext';
import useAxios from "../../utils/useAxios";


export default function User(){
    const api = useRef(useAxios())
    const { Search } = Input;
    const [users, setUsers] = useState([])
    const [totalRecord , setTotalRecord] = useState(0)
    const [selectedRowKeys, setSelectedRowKeys] = useState([]);
    const {messageApi} = useContext(AuthContext)
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
    const [filterDict, setFilterDict] =useState({page:1,pageSize:10,orderBy:"-id",search:""})
    const [selectedRows ,setSelectedRows] = useState([])
    const [isEdit, setIsEdit] = useState(false);
    const [passValid, setPassValid] = useState(true)
    const [groups, setGroups] = useState([])
    const [matchPassValid, setMatchPassValid] = useState(true)
    let register_payload = {first_name:"", last_name:"", email:"", mobile:"", groups:"", password:"", confirm_password:"", is_active:true}
    const [registerForm, setRegisterForm] = useState(register_payload)
    const usernameRegex = /^[a-zA-Z0-9_]{3,20}$/;
    const passwordRegex = /^(?=.*\d)(?=.*[a-z])(?=.*[\W_])(?=.*[A-Z]).{6,20}$/

    const handleChange= (e) => {
        setRegisterForm({...registerForm,[e.target.name]:e.target.value})
        if(e.target.name === "password"){
            setPassValid(passwordRegex.test(e.target.value)?true:false)
        }
        if(e.target.name === "confirm_password"){
            setMatchPassValid(registerForm.password === e.target.value?true:false)
        }
    }

    const registerUser = async() => {
        var usernameValid = usernameRegex.test(registerForm.username)? true:false
        var passwordValid = registerForm.password === registerForm.confirm_password?true:false
        if((isEdit && usernameValid) || (passwordValid && usernameValid)){

            const url_ = isEdit ? `/account/register/?id=${registerForm.id}` : `/account/register/`

            await api.current.post(url_, {registerForm})
            .then((res)=>{
                if(res.data.status === 0){
                    messageApi.open({type: 'error', content:res.data.message})
                }else{
                    setIsModalOpen(false)
                    getUserData();
                    messageApi.open({type: 'success', content:res.data.message})
                }
            })
            .catch((error)=>{
                messageApi.open({type: 'error', content:error.message})
            })


        }else{
            setMatchPassValid(passwordValid)
            console.log("Something went Wrong on registration")
            return 0
        }
    }


    let getUserData = useCallback(async () =>{
        await api.current.get(`/qr_admin/user_list/?page=${filterDict.page}&page_size=${filterDict.pageSize}&ordering=${filterDict.orderBy}&search=${filterDict.search}`,
            )
            .then((res)=>{
                setTotalRecord(res.data.count)
                setUsers(res.data.results)
            })
            .catch((error)=>{
                messageApi.open({type: 'error',content: error.message})
            })
    },[filterDict, messageApi])

     const getGroup = useCallback(async()=>{
            await api.current.get('/manager/group_permission/')
            .then((res)=>{
                setGroups(res.data.data)
            }).catch((error)=>{
                messageApi.open({type: 'error',content: error.message})
            })
    },[messageApi])

    useEffect(()=>{
        getUserData();
    }, [getUserData])


    const columns = [
        {title:"First Name",dataIndex:"first_name",sorter: true},
        {title:"Last name",dataIndex:"last_name",sorter: true},
        {title:"Email",dataIndex:"email",sorter: true},
        {title:"Is active",dataIndex:"is_active", sorter: true,
            render: (is_active) => {
                const color = is_active ? 'green' : 'volcano';
                const tag = is_active ? 'Active' : 'Inactive';

                return (
                <Tag color={color} key={tag}>
                    {tag.toUpperCase()}
                </Tag>
                );
            }
        },
        {title:"Last Login",dataIndex:"last_login", sorter: true},
        {title:"Group", dataIndex:"group__name", sorter: true},
    ]

    const onSelectChange =(newSelectedRowKeys)=>{
        setSelectedRows(selectedRows)
        setSelectedRowKeys(newSelectedRowKeys)
    }



    const onTableChange = (pagination, filters, sorter) =>{
        var orderBy = sorter.order ? (sorter.order === "ascend"? "":"-") + sorter.field : "-id"
        setFilterDict({...filterDict,page:pagination.current,pageSize:pagination.pageSize,orderBy:orderBy})
    }

    const addUser = () =>{
        getGroup()
        setIsEdit(false)
        setRegisterForm(register_payload)
        setIsModalOpen(true)
    }

    const deleteUser = () => {
        if(selectedRowKeys.length === 1){
            setIsDeleteModalOpen(true)
        }else{
            messageApi.open({type: 'error', content:"Please select one data."})
        }
    }

    const deleteOk = useCallback(async()=>{
        await api.current.delete(`/account/register/?id=${selectedRowKeys[0]}`)
            .then((res)=>{
                if(res.data.status === 1){
                    messageApi.open({type: 'success',content: res.data.message})
                    getUserData();
                }
                else{
                    messageApi.open({type: 'error',content: res.data.message})
                }
            })
            .catch((error)=>{
                messageApi.open({type: 'error',content: error.message})
            })
            setIsDeleteModalOpen(false)
    },[messageApi, selectedRowKeys, getUserData])

    const editUser = useCallback(async() => {
        if(selectedRowKeys.length === 1){
            getGroup()
            setIsEdit(true)
            await api.current.get(`/account/register/?pk=${selectedRowKeys[0]}`)
                .then((res)=>{
                    if(res.data.status === 1){
                        let data = res.data.data[0]
                        setRegisterForm({id:data.id, email:data.email || "", first_name:data.first_name || "", last_name:data.last_name || "", mobile:data.mobile || "", groups:data.groups || "", is_active:data.is_active})
                        setIsModalOpen(true)
                    }
                    else{
                        messageApi.open({type: 'error',content: res.data.message})
                    }
                })
                .catch((error)=>{
                    messageApi.open({type: 'error',content: error.message})
                })

        }else{
            messageApi.open({type: 'error', content:"Please select one data."})
        }
    },[messageApi, selectedRowKeys, getGroup])



    return(
    <>
       <div className='title_tab'>
            <div className='title_tab_title'>Users</div>
            <div className="title_tab_div">
                <Search placeholder="Search by name, email" allowClear={true} onChange={(e)=> {if(e.target.value===""){setFilterDict({...filterDict, search:""})}}} onSearch={(value) => setFilterDict({...filterDict, search:value})} style={{ width: 200 }} />
                <Button type="primary" onClick={addUser}>Add</Button>
                <Button type="primary" onClick={editUser}>Edit</Button>
                <Button type="primary" onClick={deleteUser}>Delete</Button>
            </div>
        </div>
        <div className='main_tab'>
        <Table
            columns={columns}
            dataSource={users} rowKey="id"
            onChange={onTableChange}
            rowSelection={{selectedRowKeys,onChange: onSelectChange}}
            pagination={{total: totalRecord,
                defaultPageSize: 10, showSizeChanger: true,
                pageSizeOptions: ['10', '20', '50', '100'],
            }}
            footer={() => ( <div style={{textAlign:'right'}}>Selected Records ({selectedRowKeys.length} of {totalRecord})</div>)}
            scroll={{ x: '75pc' }}
            size="small"/>
        </div>
        <Modal title="Add User" open={isModalOpen} okText="Create" footer={[
            <Button form="registerForm" key="submit" htmlType="submit">Submit</Button>]} onCancel={()=>setIsModalOpen(false)} >
            <Form id="registerForm" labelCol={{flex: '150px'}} onFinish={registerUser} labelAlign="left" autoComplete="off">
                <Form.Item label="Email (username)">
                    <input type="email" name="email" value={registerForm.email} onChange={handleChange} className="input_field" autoComplete="new-email" required/>
                </Form.Item>
                <Form.Item label="First name">
                    <input type='text' name="first_name" value={registerForm.first_name} onChange={handleChange} required></input>
                </Form.Item>
                <Form.Item label="Last name">
                    <input type='text' name="last_name" value={registerForm.last_name} onChange={handleChange} required></input>
                </Form.Item>
                <Form.Item label="Mobile no.">
                    <input type='number' name="mobile" value={registerForm.mobile} onChange={handleChange} required></input>
                </Form.Item>
                <Form.Item label="Is active">
                    <input type='checkbox' name="is_active" checked={registerForm.is_active} onChange={(e)=>setRegisterForm({...registerForm, is_active:e.target.checked})}></input>
                </Form.Item>
                <Form.Item label="Group">
                        <select name="groups" id="select_value" value={registerForm.groups} onChange={handleChange} style={{width:'182px'}}>
                            <option >-----</option>
                            {groups.map((data)=>(
                                <option key={data.id} value={data.id}>{data.name}</option>
                            ))}
                        </select>
                </Form.Item>
                { !isEdit && <>
                    <Form.Item label="Password" required>
                        <input type="password" name="password" onChange={handleChange} className="input_field" required autoComplete="new-password" />
                        <br></br>{!passValid && <span className="valid_error">It must contain at least one digit, lowercase, uppercase, special character and length between 6 and 20 characters.</span>}
                    </Form.Item>
                    <Form.Item label="Confirm password" required>
                        <input type="password" name="confirm_password" onChange={handleChange} className="input_field" required />
                        <br></br>{!matchPassValid && <span className="valid_error">Password must match.</span>}
                    </Form.Item>
                </>}
            </Form>
        </Modal>
        <Modal
            title="Delete Confirmation"
            closable={{ 'aria-label': 'Custom Close Button' }}
            open={isDeleteModalOpen}
            onOk={deleteOk}
            onCancel={()=> setIsDeleteModalOpen(false)}
        >
            Are you sure you want to delete this user ?
        </Modal>
    </>
    )
}
