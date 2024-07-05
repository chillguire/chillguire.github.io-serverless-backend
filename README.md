## To do, improvements, ideas
* Costos/mejoras seguridad
	* En el lambda al apagar/prender/hacer el schedule verificar costos y que te mantengas en el free tier
		* AWS Budgets
		* cost explorer boto3
		* aws billing, etc
  		* verificar EBS para las EC2, en cuanto a storage total e IOPS    
		* other
			* retries del eventbridge y retention time event
			* y memory requirements del lambda/timeout, ***simular costos por request***
* Seguridad
	* https://dev.to/awscommunity-asean/devs-guide-to-surviving-ddos-attacks-in-your-api-56ke
	* evitar ataques con WAF?
 	* cloudflare tiene free tier
	* rate limit api, etc
	* proteger/limitar con cognito
		* https://docs.aws.amazon.com/location/latest/developerguide/authenticating-using-cognito.html
	* Mejorar roles/policies en cuanto a resources, limitar por region, recurso/servicio, cuenta (?)
* template del EC2 con SSL/HTTPS
	* https://bansalanuj.com/https-aws-ec2-without-custom-domain
	* https://gist.github.com/marianocordoba/cea09031a25d55365811f54aebd4bbef
