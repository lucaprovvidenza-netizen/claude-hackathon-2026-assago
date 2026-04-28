package com.brennero.portal;

import org.apache.catalina.Context;
import org.apache.catalina.startup.Tomcat;
import org.apache.catalina.WebResourceRoot;
import org.apache.catalina.webresources.DirResourceSet;
import org.apache.catalina.webresources.StandardRoot;
import org.apache.tomcat.util.descriptor.web.FilterDef;
import org.apache.tomcat.util.descriptor.web.FilterMap;

import javax.servlet.DispatcherType;
import java.io.File;

/**
 * Launcher per Tomcat embedded.
 * Avvia il portale su http://localhost:8080/
 */
public class PortalLauncher {

    public static void main(String[] args) throws Exception {
        Tomcat tomcat = new Tomcat();
        tomcat.setPort(8080);

        // Temp dir per compilazione JSP
        String baseDir = new File(System.getProperty("java.io.tmpdir"), "brennero-tomcat").getAbsolutePath();
        tomcat.setBaseDir(baseDir);
        tomcat.getConnector();

        // Webapp directory - usa addContext per evitare problemi classloader con web.xml
        String webappDir = new File("src/main/webapp").getAbsolutePath();
        Context ctx = tomcat.addContext("", webappDir);

        // Configura classloader per JSP e servlet
        ctx.setParentClassLoader(PortalLauncher.class.getClassLoader());

        // Registra Jasper initializer per JSP
        ctx.addServletContainerInitializer(new org.apache.jasper.servlet.JasperInitializer(), null);

        // Registra JSP servlet
        Tomcat.addServlet(ctx, "jsp", new org.apache.jasper.servlet.JspServlet());
        ctx.addServletMappingDecoded("*.jsp", "jsp");

        // Registra il PortalServlet
        Tomcat.addServlet(ctx, "portal", new PortalServlet());
        ctx.addServletMappingDecoded("/portal", "portal");

        // Registra il default servlet per file statici (CSS, ecc.)
        Tomcat.addServlet(ctx, "default",
            new org.apache.catalina.servlets.DefaultServlet());
        ctx.addServletMappingDecoded("/", "default");

        // Registra AuthFilter
        FilterDef filterDef = new FilterDef();
        filterDef.setFilterName("AuthFilter");
        filterDef.setFilterClass("com.brennero.portal.AuthFilter");
        ctx.addFilterDef(filterDef);

        FilterMap filterMap = new FilterMap();
        filterMap.setFilterName("AuthFilter");
        filterMap.addURLPattern("/*");
        ctx.addFilterMap(filterMap);

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
