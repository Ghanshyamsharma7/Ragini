import  { createContext, useState, useEffect } from "react";
import API from "../api/api";

export const AuthContext = createContext();

export function AuthProvider({ children }) {

  const [user,setUser] = useState(null);

  const fetchUser = async () => {
    try{
      const res = await API.get("/auth/me");
      setUser(res.data);
    }catch(err){
      setUser(null);
    }
  };

  useEffect(()=>{
    fetchUser();
  },[]);

  return (
    <AuthContext.Provider value={{user,setUser}}>
      {children}
    </AuthContext.Provider>
  );
}