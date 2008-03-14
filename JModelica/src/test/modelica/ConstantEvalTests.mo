package ConstantEvalTests
	
	model CEvalTest1 
		model M
		 model A 
   Real x=1;
   Real y=2;
  end A;
  
  model B 
   A a;
   Real z;
  end B;
  
  model C 
   B b(z=u);
   Real u=b.a.x;
  end C;
  
  C c1;
  C c2(u=p,b(z=c1.u,a(x=c1.b.a.y)));
  parameter Real p=1;
	
		end M;
	    M m;
	end CEvalTest1;

	
	model CEvalTest2 
	
	/*
	fclass ConstantEvalTests.CEvalTest2
 Real m.c1.b.a.x = 1;
 Real m.c1.b.a.y = 2;
 Real m.c1.b.z = m.c1.u;
 Real m.c1.u = m.c1.b.a.x;
 Real m.c2.b.a.x = m.c1.b.a.y;
 Real m.c2.b.a.y = 2;
 Real m.c2.b.z = m.c1.u;
 Real m.c2.u = m.p;
 parameter Real m.p = 1;
equation 
end ConstantEvalTests.CEvalTest2;
	
	
	*/
		model M
		 model A0
			Real x=1;
   			Real y=2;
  		 end A0; 
		
		 model A
		 	extends A0; 
   		end A;
  
  		model B 
   			A a;
   			Real z;
  		end B;
  
  		model C 
   			B b(z=u);
   			Real u=b.a.x;
  		end C;
  
  		C c1;
  		C c2(u=p,b(z=c1.u,a(x=c1.b.a.y)));
  		parameter Real p=1;
	
		end M;
	    M m;
	end CEvalTest2;
	
	

end ConstantEvalTests;