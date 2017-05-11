/*********************************************
 * OPL 12.6.2.0 Model
 * Author: Tal Raviv
 * Creation Date: 18 Apr 2017 at 11:13:52
 *********************************************/
 
int nOrders = ...; 
range Days = 1..6;
range Orders = 1..nOrders;
range Sites = 0..nOrders;
range Sched = 1..12;
 
{int} R = {1,2,3,6};
 
{int} P[R] = [{1},{2,3},{4,5,6},{7,8,9,10,11,12}];
 
{int} D[Days] =[{1,2,4,7}, {1,3,5,8}, {1,2,6,9}, {1,3,4,10}, {1,2,5,11}, {1,3,6,12}] ;
 
int Rt[Orders] = ...;   // Rhytems 
 
float C = ...;       // Vehicle Capacity
float G = ...;       // Maximum Shift Length
float w[Orders] = ...;       // Order's Weight
float st[Sites] = ...;      // Order's Service Time
float t[Sites][Sites] = ...;  // Time from Site to Site
  
dvar boolean y[Orders][Sched];   // order is srved by a sched
dvar boolean x[Days][Sites][Sites];
dvar float+ s[Days][Sites];
dvar float+ f[Days][Sites];

dvar float+ total_service_time;

execute { cplex.tilim = 1000; }
 
minimize sum (i in Sites, j in Sites: j!=i) sum (d in Days) x[d,i,j]*(t[i,j]+st[i]);
  subject to { 
 	
 	total_service_time == sum (i in Sites, j in Sites: j!=i)  sum (d in Days) x[d,i,j]*st[i]; 
 	
 	forall (i in Orders) sum(p in P[Rt[i]]) y[i,p]  == 1;
 	//forall (i in Orders) sum(p in Sched) y[i,p]  == 1;
 	
 
 	forall( i in Orders, d in Days) sum(j in Sites : j != i) x[d,i,j] 
 	  == sum(p in D[d]) y[i,p];
 	  
 	forall (i in Sites, d in Days) sum (j in Sites) x[d,i,j] == sum (j in Sites) x[d,j,i];
 	
 	forall (d in Days) f[d,0] == 0;
 	
 	forall (i in Sites, j in Orders: j!=i, d in Days) f[d,j] >= f[d,i] + w[j] - C*(1-x[d,i,j]);
 	
 	forall (i in Orders, d in Days) f[d,i] <= C;
 	
 	forall (i in Sites, j in Orders: j!=i, d in Days) s[d,j] >= s[d,i] + st[i] + t[i,j] - G*(1-x[d,i,j]);
 	
 	forall (i in Orders, d in Days) s[d,i] + st[i] + t[i,0] <= G;
 	   
 }
 
 execute {
 	for (var d in Days) {
 		writeln("Routes of day ",d); 	
 		for (var k in Orders) if (x[d][0][k] > 0.5) {
 			write("0 -> ", k );
 			var curr_order = k;
 			while (curr_order != 0) {
 				for (var i in Sites) if (x[d][curr_order][i] > 0.5) {
 					write(" -> ", i); 	
 					curr_order = i;
 					break;
   				} 				
  			} 
  			writeln(" ");					
  		} 
  		writeln(" ");	
 	} 
	writeln(y); 
}
 
 