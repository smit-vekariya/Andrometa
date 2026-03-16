import { useCallback, useEffect, useRef, useState,useContext } from "react"
import useAxios from "../../utils/useAxios"
import { AuthContext } from "../../context/AuthContext";
import { Button, Input, Table,Modal,Form } from "antd";
const {TextArea }= Input



export default function SystemParameter(){
    const api = useRef(useAxios())
    const {messageApi} = useContext(AuthContext)
    const [systemParameterData, setSystemParameterData] = useState([])
    const [selectedRowKeys, setSelectedRowKeys] = useState([]);
    const [selectedRows ,setSelectedRows] = useState([])
    const [totalRecord , setTotalRecord] = useState(0)
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isEdit, setIsEdit] = useState(false);
    const filter_dict = {page:1,pageSize:10,orderBy:"-id",search:"",top:0}
    const initialValues = {"id":0,"code":"","value":"","description":""}
    const [form_data, setForm]  = useState(initialValues)
    const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
    const [filterDict, setFilterDict] =useState(filter_dict)

    const getSysParameter = useCallback(async()=>{
        await api.current.get(`/manager/sys_parameter/`)
            .then((res)=>{
                setTotalRecord(res.data.data.length)
                setSystemParameterData(res.data.data)
            })
            .catch((error)=>{
                messageApi.open({type: 'error', content:error.message})
            })

    },[messageApi])

    useEffect(()=>{
        getSysParameter()
    },[getSysParameter])

    const columns = [
        {title:"Code", dataIndex:"code", sorter: true},
        {title:"Value", dataIndex:"value", sorter: true},
        {title:"Description", dataIndex:"description", sorter: true}
    ]


    const onTableChange = (pagination, filters, sorter) =>{
        var orderBy = sorter.order ? (sorter.order === "ascend"? "":"-") + sorter.field : "-id"
        setFilterDict({...filterDict,page:pagination.current,pageSize:pagination.pageSize,orderBy:orderBy})
    }

    const addSysPara = () =>{
        setIsEdit(false)
        setForm(initialValues)
        setIsModalOpen(true)
    }
    const editSysPara = ()=>{
        if(selectedRows.length === 1){
            setForm(selectedRows[0])
            setIsEdit(true)
            setIsModalOpen(true)
        }else{
            messageApi.open({type: 'error', content:"Please select one data."})

        }
    }

    const deleteSysPara = () => {
        if(selectedRowKeys.length === 1){
            setIsDeleteModalOpen(true)
        }else{
            messageApi.open({type: 'error', content:"Please select one data."})
        }
    }

    const deleteOk = useCallback(async()=>{
        await api.current.delete(`/manager/sys_parameter/${selectedRowKeys[0]}/`)
            .then((res)=>{
                if(res.data.status === 0){
                    messageApi.open({type: 'error', content:res.data.message})
                }else{
                    getSysParameter()
                    messageApi.open({type: 'success', content:res.data.message})
                }
            })
            .catch((error)=>{
                messageApi.open({type: 'error', content:error.message})

            })
            setIsDeleteModalOpen(false)
    },[messageApi, selectedRowKeys, getSysParameter])

    const handleOk = useCallback(async() =>{
        await api.current.post(`/manager/sys_parameter/`,{form_data})
        .then((res)=>{
            if(res.data.status === 0){
                messageApi.open({type: 'error', content:res.data.message})
            }else{
                getSysParameter()
                messageApi.open({type: 'success', content:res.data.message})
            }
        })
        .catch((error)=>{
            messageApi.open({type: 'error', content:error.message})

        })
        setIsModalOpen(false)
    },[form_data,messageApi,getSysParameter])

    const onSelectChange =(newSelectedRowKeys, selectedRows)=>{
        setSelectedRows(selectedRows)
        setSelectedRowKeys(newSelectedRowKeys)
    }

    const handleEdit =  useCallback(async() =>{
        await api.current.put(`/manager/sys_parameter/${selectedRowKeys[0]}/`,{form_data})
            .then((res)=>{
                if(res.data.status === 0){
                    messageApi.open({type: 'error', content:res.data.message})
                }else{
                    getSysParameter()
                    messageApi.open({type: 'success', content:res.data.message})
                }
            })
            .catch((error)=>{
                messageApi.open({type: 'error', content:error.message})
            })
            setIsModalOpen(false)
    },[form_data,selectedRowKeys,getSysParameter,messageApi])


    return (<>
            <div className='title_tab'>
                <div className='title_tab_title'>System Parameter</div>
                <div className="title_tab_div">
                    <Button type="primary" onClick={addSysPara}>Add</Button>
                    <Button type="primary" onClick={editSysPara}>Edit</Button>
                    <Button type="primary" onClick={deleteSysPara}>Delete</Button>
                </div>
            </div>
            <div className='report_tab'>
                <p style={{color:"burlywood"}}>This code and value use as global variable in project which can be change as needed. For Example : Set credential of sending email, Set point per amount(which can be change)</p>
            </div>
            <div className="main_tab">
                <Table
                    columns={columns}
                    dataSource={systemParameterData} rowKey="id"
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
            <Modal title="Add System Parameter" open={isModalOpen} okText="Create" footer={[
                <Button form="myForm" key="submit" htmlType="submit">Submit</Button>]} onCancel={()=>setIsModalOpen(false)}>
                <Form id="myForm" labelCol={{flex: '110px'}} onFinish={isEdit ? handleEdit : handleOk} labelAlign="left">
                    <Form.Item label="Code">
                        <input type='text' name="code" value={form_data.code} onChange={(e) => setForm({...form_data, code:e.target.value})} required></input>
                    </Form.Item>
                    <Form.Item label="Value">
                        <input type='text' name="value" value={form_data.value} onChange={(e) => setForm({...form_data, value:e.target.value})} required></input>
                    </Form.Item>
                    <Form.Item label="Description">
                        <TextArea name="description" value={form_data.description}  onChange={(e) => setForm({...form_data, description:e.target.value})} required/>
                    </Form.Item>
                </Form>
            </Modal>
            <Modal
                title="Delete Confirmation"
                closable={{ 'aria-label': 'Custom Close Button' }}
                open={isDeleteModalOpen}
                onOk={deleteOk}
                onCancel={()=> setIsDeleteModalOpen(false)} 
            >
                Are you sure you want to delete this parameter ?
            </Modal>
    </>)
}