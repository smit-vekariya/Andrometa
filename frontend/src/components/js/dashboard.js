import { LogoutOutlined, UserOutlined } from '@ant-design/icons';
import { Dropdown, Flex, Layout, Menu, Spin } from 'antd';
import 'font-awesome/css/font-awesome.min.css';
import React, { createContext, memo, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { Link, Outlet } from "react-router-dom";
import { AuthContext } from '../../context/AuthContext';
import "../CustomAntd.css";
import "../component.css";
import logo_char from '../images/favicon.ico';
import Email from './Email';

export const DashboardContext = createContext();
const baseURL = process.env.REACT_APP_BASE_URL
const { Header, Content, Footer, Sider } = Layout;
function getItem(label, key, icon, children) {
  return {
    key,
    icon,
    children,
    label,
  };
}
const Dashboard = () => {
  const {authTokens} = useContext(AuthContext)
  const current = window.location.pathname
  const {user,logoutUser, messageApi} = useContext(AuthContext)
  let [loading, setLoading] = useState(false)
  const [collapsed, setCollapsed] = useState(false);
  const [menuData, setMenuData] = useState(()=>localStorage.getItem("main_menu") ? JSON.parse(localStorage.getItem("main_menu")):{});


  let getMainMenu = useCallback(async () =>{
    let response = await fetch(`${baseURL}/account/main_menu/`,{
      method:"GET",
      headers:{
          'Content-Type':"application/json",
          'Authorization':`Bearer ${authTokens?.access}`
      },
    })
    let data = await response.json()
    if (data.status === 1){
        setMenuData(data.data)
        localStorage.setItem("main_menu", JSON.stringify(data.data))
    }else{
        messageApi.open({type: 'error',content: data.message})
    }
  },[messageApi,authTokens])

  useEffect(() => {
      getMainMenu()
  },[getMainMenu])


  const menu_items = useMemo(()=>{
    var new_list = []
    var nested_list = []
    var parent = null
    for(let [key,v] of Object.entries(menuData)){
        let k = parseInt(key)
        if(menuData[k+1]){
          if ((v.sequence).split(".")[0] === ((menuData[k+1]).sequence).split(".")[0]){
            parent = parent === null ? k : parent
            nested_list.push(getItem(<Link to={menuData[k+1].url}>{menuData[k+1].name}</Link>, menuData[k+1].url,<i className={menuData[k+1].icon} />))
          }else{
            if(parent != null){
              new_list.push(getItem(menuData[parent].name, menuData[parent].url, <i className={menuData[parent].icon} /> ,nested_list))
              parent = null
              nested_list =[]
            }else{
              // below line is use full, remove temporary for bond click requirement and add new line that second from below line
              // new_list.push(getItem(v.name, v.url, <i className={v.icon} />))
              new_list.push(getItem(<Link to={v.url}>{v.name}</Link>, v.url, <i className={v.icon} />))
            }
          }
        }else{
          new_list.push(getItem(<Link to={v.url}>{v.name}</Link>, v.url, <i className={v.icon} />))
        }
    }

    // let fixed_items = [getItem((<img src={logo_char} alt="logo-no-background.png" style={{width:"20px"}}></img>), '0', (collapsed ? <img src={logo_char} alt="logo-char.png" style={{width:"20px"}}></img>:""))]
    let fixed_items = [getItem(<h2 style={{fontFamily: 'system-ui', margin:'0px', fontSize: '25px', color:"#0087ff"}}>PanelPrime</h2>, '0', (collapsed ? <img src={logo_char} alt="logo-char.png" style={{width:"20px"}}></img>:""))]
    let final_menu_items  =[...fixed_items,...new_list]
    return final_menu_items
  },[menuData,collapsed])

  return (
    <Layout style={{minHeight: '100vh'}}>
      <SideBar collapsed={collapsed} menuItems={menu_items} current={current} onCollapse={useCallback((value)=>setCollapsed(value),[])}/>
      <Layout>
        <HeaderBar logoutUser={logoutUser} user={user} setLoading={setLoading}/>
        <Content className='content_class'>
          <DashboardContext.Provider value={{setLoading:setLoading}}>
            <Spin spinning={loading}>
              <Outlet/>
            </Spin>
          </DashboardContext.Provider>
        </Content>
        <Footer style={{textAlign: 'center'}}>
        </Footer>
      </Layout>
    </Layout>
  );
};
export default Dashboard;


const SideBar = memo(({collapsed, menuItems, onCollapse, current}) =>{
  return (
    <Sider collapsible collapsed={collapsed} onCollapse={onCollapse} className="custom_sidebar">
      <Menu defaultSelectedKeys={[current]} mode="inline" items={menuItems} />
    </Sider>
  )
});

const HeaderBar = memo(({logoutUser, user, setLoading})=>{
  const items = [
    getItem((<Link to="/profile">My Profile</Link>), '1', <UserOutlined />),
    // getItem((<Link to="/register">Register</Link>), '2', <UserAddOutlined />),
    getItem((<Link onClick={logoutUser}>Logout</Link>), '3', <LogoutOutlined />),
  ];

  return (
      <Header className='custom_header'>
          <DashboardContext.Provider value={{setLoading:setLoading}}>
            <Email/>
          </DashboardContext.Provider>
          <Flex gap="small" wrap="wrap" style={{float: "right", marginRight:"10px"}}>
              <Dropdown.Button menu={{items}} style={{margin: "9px 0px 5px 1px"}} placement="bottomLeft" icon={<UserOutlined />}>{user && user.full_name}</Dropdown.Button>
          </Flex>
      </Header>
  )
})