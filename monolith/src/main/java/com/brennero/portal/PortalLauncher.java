package com.brennero.portal;

import org.apache.catalina.Context;
import org.apache.catalina.startup.Tomcat;
import org.apache.catalina.WebResourceRoot;
import org.apache.catalina.webresources.DirResourceSet;
import org.apache.catalina.webresources.StandardRoot;

import java.io.File;

/**
 * Launcher per Tomcat embedded.
 * Avvia il portale su http://localhost:8080/portal
 */
public class PortalLauncher {

    public static void main(String[] args) throws Exception {
        Tomcat tomcat = new Tomcat();
        tomcat.setPort(8080);
        tomcat.getConnector();

        // Webapp directory
        String webappDir = new File("src/main/webapp").getAbsolutePath();
        Context ctx = tomcat.addWebapp("", webappDir);

        // Classes directory
        WebResourceRoot resources = new StandardRoot(ctx);
        File classesDir = new File("target/classes");
        if (classesDir.exists()) {
            resources.addPreResources(new DirResourceSet(resources,
                "/WEB-INF/classes", classesDir.getAbsolutePath(), "/"));
        }
        ctx.setResources(resources);

        System.out.println("===========================================");
        System.out.println(" Brennero Logistics - Portale Ordini");
        System.out.println(" http://localhost:8080/");
        System.out.println(" Login: admin / admin123");
        System.out.println("===========================================");

        tomcat.start();
        tomcat.getServer().await();
    }
}
