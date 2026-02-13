import {
  NavigationMenu,
  NavigationMenuList,
  NavigationMenuItem,
  NavigationMenuLink,
} from "@/components/ui/navigation-menu";
import { FaSignOutAlt } from "react-icons/fa";
import {
  Breadcrumb,
  BreadcrumbSeparator,
  BreadcrumbList,
  BreadcrumbItem,
  BreadcrumbLink,
  // BreadcrumbPage,
} from "@/components/ui/breadcrumb";
import logo_polban from "../../assets/logo/polban.png";
import { useNavigate  } from "react-router-dom";


type NavbarProps = {
  screenName?: string;
};
const NavbarForm: React.FC<NavbarProps> = ({
  screenName = "Screen Name"
}) => {
  const navigate = useNavigate();

  const handleBack = () => {
    navigate(-1)
  };

  return (
    <nav
      className="relative top-0 left-0 right-0 z-10 flex items-center justify-between px-4 py-2"
      style={{ backgroundColor: "#2140AD" }}
    >
      <div className="flex items-center">
        {/* Logo */}
        <img
          src={logo_polban}
          alt="Polban Logo"
          className="w-10 h-10 lg:w-12 lg:h-12 mr-1 lg:mr-4"
        />

        <NavigationMenu>
          <NavigationMenuList>
            <NavigationMenuItem>
              <NavigationMenuLink
                href="/Home"
                className="block px-1 lg:px-2 py-0 lg:py-2 text-sm lg:text-xl font-medium text-white hover:text-black"
              >
                Coverage Test
              </NavigationMenuLink>
            </NavigationMenuItem>
            <Breadcrumb className="flex items-center ml-4">
              <BreadcrumbSeparator className="text-white text-xl mx-2">
                |
              </BreadcrumbSeparator>
              <BreadcrumbList>
                <BreadcrumbItem>
                  <BreadcrumbLink>
                    <span className="text-white text-xs lg:text-sm hover:text-gray-300">
                      {screenName}
                    </span>
                  </BreadcrumbLink>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </NavigationMenuList>
        </NavigationMenu>
      </div>

      <a
        href="#"
        onClick={handleBack}
        className="flex items-center text-white hover:text-gray-300 mr-8"
      >
        <FaSignOutAlt size={18} className="mr-0 md:mr-2" />
        <span className="hidden md:inline text-base">Kembali</span>
      </a>
    </nav>
  );
}

export default NavbarForm;